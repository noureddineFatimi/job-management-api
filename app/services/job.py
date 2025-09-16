from models.models import OffreEmploi, Competence, Candidature, Entreprise, Candidature, User, Ville, Fonction, SecteurActivite
from shemas.job import OffreIn, ApplyIn, CompetencesIn
from datetime import datetime, timezone, timedelta
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi import Depends
from sqlalchemy import desc, func, extract
from huggingface_hub import InferenceClient
from config import ACCESS_TOKEN_HUGGING_FACE

gmt_plus_1_timezone = timezone(timedelta(hours=1))

def get_nombre_offres_publies(current_user, db: Session = Depends(get_db)):
    return db.query(OffreEmploi).filter(OffreEmploi.user_id == current_user.id).count()

def get_nombre_candidatures_recues(current_user, db: Session = Depends(get_db)):
    total = db.query(func.sum(OffreEmploi.nbr_candidats)).filter(OffreEmploi.user_id == current_user.id).scalar()
    return total or 0

def get_nombre_employes_a_recruter(current_user, db: Session = Depends(get_db)):
    total = db.query(func.sum(OffreEmploi.nbr_employes_demande)).filter(OffreEmploi.user_id == current_user.id).scalar()
    return total or 0

def get_repartition_par_type_de_contrat(current_user, db: Session = Depends(get_db)):
    return db.query(OffreEmploi.type_offre, func.count(OffreEmploi.id)).filter(OffreEmploi.user_id == current_user.id).group_by(OffreEmploi.type_offre).all()

def repartition_par_secteurs_activite(current_user, db: Session = Depends(get_db)):
    return db.query(SecteurActivite.nom_secteur, func.count(OffreEmploi.id)).join(SecteurActivite, OffreEmploi.secteur_activite_id == SecteurActivite.id).filter(OffreEmploi.user_id == current_user.id).group_by(SecteurActivite.nom_secteur).all()

def repartition_par_mois_annee_courante(current_user, db: Session = Depends(get_db)):
    current_year = datetime.now().year
    results = (
        db.query(extract("month", OffreEmploi.created_at).label("mois"),func.count(OffreEmploi.id).label("nombre")).filter(OffreEmploi.user_id == current_user.id,extract("year", OffreEmploi.created_at) == current_year).group_by("mois").order_by("mois").all())
    liste_des_mois = [{"mois": int(mois), "nombre": nombre} for mois, nombre in results]
    mois_existants = {obj["mois"] for obj in liste_des_mois}
    for i in range(1, 13):
        if i not in mois_existants:
            liste_des_mois.append({"mois": i, "nombre": 0})
    liste_des_mois.sort(key=lambda x: x["mois"])
    return liste_des_mois

def filter_offres(mot_cle: Optional[str] = None, secteur_activite_id: Optional[int] = None, fonction_id: Optional[int] = None, ville_id: Optional[int] = None, annees_experience_min: Optional[int] = None, types_offre: Optional[list[str]] = None, limit: int = 10, offset: int = 0,db: Session = Depends(get_db)):
    offres = db.query(OffreEmploi)
    if mot_cle:
        offres = offres.filter(OffreEmploi.titre.ilike(f"%{mot_cle}%"))
    if secteur_activite_id:
        offres = offres.filter(OffreEmploi.secteur_activite_id == secteur_activite_id)
    if fonction_id:
        offres = offres.filter(OffreEmploi.fonction_id == fonction_id)
    if ville_id: 
        offres = offres.filter(OffreEmploi.ville_id == ville_id)
    if annees_experience_min:
        offres = offres.filter(OffreEmploi.annees_experience_min >= annees_experience_min)
    if types_offre:
        offres = offres.filter(OffreEmploi.type_offre.in_(types_offre)) 
    total = offres.count()
    offres = offres.order_by(desc(OffreEmploi.deadline_postulation)).offset(offset).limit(limit).all()
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

def generate_resume(description:str):
    client = InferenceClient(provider="hf-inference",api_key=ACCESS_TOKEN_HUGGING_FACE)
    result = client.summarization(description,model="facebook/bart-large-cnn")
    return result.summary_text

def create_and_flush_offre(offre: OffreIn, entreprise: Entreprise ,current_user:  User, db: Session = Depends(get_db)):
    resume = generate_resume(offre.description)
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
            description=offre.description,
            deadline_postulation=offre.deadline_postulation,
            resume=resume
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

def recuperer_villes_fct_secteurs(db: Session = Depends(get_db)):
    ressources = {"villes": [], "fonctions": [], "secteurs_activite": []}
    ressources["villes"] = db.query(Ville).all()
    ressources["fonctions"] = db.query(Fonction).all()
    ressources["secteurs_activite"] = db.query(SecteurActivite).all()
    return ressources

def check_candidature_exist(candidature: ApplyIn, id_offre: int, db: Session = Depends(get_db)):
    return db.query(Candidature).filter(Candidature.id_offre == id_offre).filter(Candidature.email == candidature.email).first() is not None

def create_and_save_candidature(offre: OffreEmploi, candidature: ApplyIn, db : Session =  Depends(get_db)):
    c = Candidature(id_offre = offre.id, nom = candidature.nom.lower().capitalize(), prenom = candidature.prenom.lower().capitalize(), cv_id = candidature.cv_id, email = candidature.email, numero_tel = candidature.numero_tel)
    db.add(c)
    offre.nbr_candidats = offre.nbr_candidats + 1
    db.commit()
    db.refresh(c)
    return c

def get_applications(id_offre: int, db : Session =  Depends(get_db)):
    return db.query(Candidature).filter(Candidature.id_offre == id_offre)