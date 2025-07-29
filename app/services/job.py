from models.models import OffreEmploi, Competence, Candidature, Entreprise, Candidature, User
from shemas.job import OffreIn, ApplyIn, CompetencesIn
from datetime import datetime, timezone, timedelta
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi import Depends

gmt_plus_1_timezone = timezone(timedelta(hours=1))

def filter_offres(secteur_activite_id: Optional[int] = None, fonction_id: Optional[int] = None, ville_id: Optional[int] = None, annees_experience_min: Optional[int] = None, type_offre: Optional[str] = None, limit: int = 10, offset: int = 0,db: Session = Depends(get_db)):
    offres = db.query(OffreEmploi)
    if secteur_activite_id:
        offres = offres.filter(OffreEmploi.secteur_activite_id == secteur_activite_id)
    if fonction_id:
        offres = offres.filter(OffreEmploi.fonction_id == fonction_id)
    if ville_id: 
        offres = offres.filter(OffreEmploi.ville_id == ville_id)
    if annees_experience_min:
        offres = offres.filter(OffreEmploi.annees_experience_min >= annees_experience_min)
    if type_offre:
        offres = offres.filter(OffreEmploi.type_offre == type_offre)
    total = offres.count()
    offres = offres.offset(offset).limit(limit).all()
    return {"total": total, "offres": offres}

def get_offres_of_user(current_user, db: Session = Depends(get_db)):
    return db.query(OffreEmploi).filter(OffreEmploi.user_id == current_user.id)

def check_offre_exist(id_offre:int, db: Session = Depends(get_db)):
    return db.query(OffreEmploi).get(id_offre)

def create_and_flush_entreprise(offre: OffreIn, db: Session = Depends(get_db)):
    entreprise = Entreprise(
            nom_entreprise=offre.nom_entreprise,
            logo_id=offre.fichier_id,
            ville_id=offre.ville_id_entreprise,
            adresse=offre.adresse
    )
    db.add(entreprise)
    db.flush()
    return entreprise 

def create_and_flush_offre(offre: OffreIn, entreprise: Entreprise ,current_user:  User, db: Session = Depends(get_db)):
    offre_enre = OffreEmploi(
            user_id=current_user.id,
            titre=offre.titre,
            entreprise_id=entreprise.id,
            teletravail=offre.teletravail,
            ville_id=offre.id_ville_offre,
            secteur_activite_id=offre.id_secteur_activite,
            fonction_id=offre.id_fonction,
            diplome_requis=offre.diplome_requis,
            niveau_etude_requis=offre.niveau_etude_requis,
            type_offre=offre.type_offre,
            annees_experience_min=offre.annee_experience_min,
            annees_experience_max=offre.annee_experience_max,
            nbr_employes_demande=offre.nbr_employes_demande,
            salaire_min=offre.salaire_min,
            salaire_max=offre.salaire_max,
            description=offre.description
    )
    db.add(offre_enre)
    db.flush()
    return offre_enre 

def create_and_flush_competences(competences: list[CompetencesIn], offre_enre: OffreEmploi,  db: Session = Depends(get_db)):
    if competences is not None:
        for competence in competences:
            c = Competence(
                    nom_competence=competence.nom_competence,
                    niveau=competence.niveau,
                    id_offre=offre_enre.id
                )
            db.add(c)

def update_offre(dict, offre_db: OffreEmploi, db: Session = Depends(get_db)):
    for k, v in dict.items():
        if k not in ("entreprise", "competences"):
            setattr(offre_db, k, v)
    if "entreprise" in dict and dict["entreprise"]:
        e = offre_db.entreprise
        for k, v in dict["entreprise"].items():
            setattr(e, k, v)
    if "competences" in dict:
        db.query(Competence).filter(Competence.id_offre == offre_db.id).delete()
        if dict["competences"] : 
            db.query(Competence).filter(Competence.id_offre == offre_db.id).delete()
            for competence in dict["competences"]:
                c = Competence(
                    nom_competence=competence["nom_competence"],
                    niveau=competence["niveau"],
                    id_offre=offre_db.id
                )
                db.add(c)
    offre_db.updated_at = datetime.now(gmt_plus_1_timezone)
    db.commit()
    db.refresh(offre_db)
    return offre_db

def delete_competences(id_offre, db: Session = Depends(get_db)):
    competences = db.query(Competence).filter(Competence.id_offre == id_offre)
    for competence in competences:
        db.delete(competence)
    
def delete_candidatures(id_offre, db: Session = Depends(get_db)):
    candidatures = db.query(Candidature).filter(Candidature.id_offre == id_offre)
    for candidature in candidatures:
        Path(candidature.cv.file_path).unlink()
        db.delete(candidature.cv)
        db.delete(candidature)

def delete_entreprise(offre: OffreEmploi, db: Session = Depends(get_db)):
    if offre.entreprise.logo_id != 1 :
        Path(offre.entreprise.logo.file_path).unlink()
        db.delete(offre.entreprise.logo)
    db.delete(offre.entreprise)

def delete_offre(offre: OffreEmploi, db: Session = Depends(get_db)):
    db.delete(offre)
    db.commit()

def check_candidature_exist(candidature: ApplyIn, id_offre: int, db: Session = Depends(get_db)):
    return db.query(Candidature).filter(Candidature.id_offre == id_offre).filter(Candidature.email == candidature.email).first() is not None

def create_and_save_candidature(offre: OffreEmploi, candidature: ApplyIn, db : Session =  Depends(get_db)):
    c = Candidature(id_offre = offre.id, nom = candidature.nom, prenom = candidature.prenom, cv_id = candidature.cv_id, email = candidature.email, numero_tel = candidature.numero_tel)
    db.add(c)
    offre.nbr_candidats = offre.nbr_candidats + 1
    db.commit()
    db.refresh(c)
    return c