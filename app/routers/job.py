from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Query
from models.models import User
from database.database import get_db
from shemas.job import OffreIn, OffresPaginesOut, OffreUpdate, OffreOut, ApplyIn
from typing import Optional
from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from routers.user import get_current_user 
from typing import Annotated
from services import job

router = APIRouter(tags=["offres d'emploi"])

@router.get("/offres/search", response_model=OffresPaginesOut)
def rechercher_offres_paginees(db: Session = Depends(get_db), secteur_activite_id: Optional[int] = None, fonction_id: Optional[int] = None,  ville_id: Optional[int] = None, annees_experience_min: Optional[int] = None, type_offre: Optional[str] = None, limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    result = job.filter_offres(secteur_activite_id, fonction_id, ville_id, annees_experience_min, type_offre, limit, offset, db)
    return result

@router.get("/offres/mes", response_model = list[OffreOut])
def rechercher_mes_offres(current_user: Annotated[User, Depends(get_current_user)] , db: Session = Depends(get_db)):
    offres = job.get_offres_of_user(current_user, db)
    return offres

@router.get("/offres/{id_offre}", response_model = OffreOut)
def recuperer_offre_par_id(id_offre:int, db: Session = Depends(get_db)):
    offre = job.check_offre_exist(id_offre, db)
    if not offre:
        raise HTTPException(status_code = 404, detail = "offre_non_trouvé")
    return offre

@router.post("/offres", status_code = 201)
def creer_offre(current_user: Annotated[User, Depends(get_current_user)], offre: OffreIn, db: Session = Depends(get_db)):
    try:
        entreprise = job.create_and_flush_entreprise(offre, db) 
        offre_enre = job.create_and_flush_offre(offre, entreprise, current_user, db)
        job.create_and_flush_competences(offre.competences, offre_enre, db)
        db.commit()  
        db.refresh(offre_enre)
        return {"message": "Offre insérée avec succès", "id_offre": offre_enre.id}
    except SQLAlchemyError as e:
        db.rollback() 
        raise HTTPException(status_code=400, detail="Erreur lors de l'insertion de l'offre : " + str(e))

@router.patch("/offres/{id_offre}", response_model = OffreOut)
def modifier_offre(current_user: Annotated[User, Depends(get_current_user)], id_offre: int, offre: OffreUpdate, db: Session = Depends(get_db)):
    try: 
        offre_db = job.check_offre_exist(id_offre, db)
        if not offre_db: 
            raise HTTPException(status_code=404, detail="offre_inexistant")
        update_data = offre.model_dump(exclude_unset = True)
        offre_db = job.update_offre(update_data, offre_db, db)
        return offre_db
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Erreur lors de la modification de l'offre : " + str(e))

@router.delete("/offres/{id_offre}")
def supprimer_offre(current_user: Annotated[User, Depends(get_current_user)], id_offre: int, db: Session = Depends(get_db)):
    try: 
        offre = job.check_offre_exist(id_offre, db)
        if not offre: 
            raise HTTPException(status_code = 404, detail = "offre_inexistant")
        job.delete_competences(id_offre, db)
        job.delete_candidatures(id_offre, db)
        job.delete_entreprise(offre, db)
        job.delete_offre(offre,db)
        return {"message": "offre supprimé"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Erreur lors de la suppression de l'offre : " + str(e))

@router.post("/offres/{id_offre}/postuler")
def postuler_a_offre(id_offre: int, candidature: ApplyIn, db : Session =  Depends(get_db)):
    try:
        offre = job.check_offre_exist(id_offre, db)
        if not offre: 
            raise HTTPException(status_code = 404, detail = "offre_inexistant")
        if job.check_candidature_exist(candidature, id_offre, db):
            raise HTTPException(status_code=400, detail="Vous avez déjà posté à cet offre")
        c = job.create_and_save_candidature(offre, candidature, db)
        return c
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Erreur lors de la postulation à l'offre : " + str(e))
