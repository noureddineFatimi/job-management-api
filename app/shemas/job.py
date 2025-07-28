from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from shemas.user import UserOut
import re

class VilleOut(BaseModel):
    nom_ville: Optional[str]
    
    class Config:
        from_attributes = True

class SecteurActiviteOut(BaseModel):
    nom_secteur: Optional[str]
    
    class Config:
        from_attributes = True

class FonctionOut(BaseModel):
    nom_fonction: Optional[str]
    
    class Config:
        from_attributes = True

class FileOut(BaseModel):
    file_path: Optional[str]
    file_name: Optional[str]
    file_type: Optional[str]

    class Config:
        from_attributes = True

class EntrepriseOut(BaseModel):
    nom_entreprise: Optional[str]
    adresse: Optional[str]
    logo: Optional[FileOut]
    ville: Optional[VilleOut]

    class Config:
        from_attributes = True

class CompetencesOut(BaseModel):
    nom_competence: Optional[str]
    niveau: Optional[str]

    class Config:
        from_attributes = True

class OffreOut(BaseModel):
    titre: Optional[str]
    teletravail: Optional[str]
    diplome_requis: Optional[str]
    niveau_etude_requis: Optional[str]
    type_offre: Optional[str]
    annees_experience_min: Optional[int]
    annees_experience_max: Optional[int]
    nbr_employes_demande: Optional[int]
    salaire_min: Optional[int]
    salaire_max: Optional[int]
    description: Optional[str]
    nbr_candidats: Optional[int]
    created_at: Optional[datetime]
    user: Optional[UserOut]
    entreprise: Optional[EntrepriseOut]
    ville: Optional[VilleOut]
    secteur_activite: Optional[SecteurActiviteOut]
    fonction: Optional[FonctionOut]
    competences: Optional[list[CompetencesOut]]

    class Config:
        from_attributes = True

class OffresPaginesOut(BaseModel):
    total: Optional[int]
    offres: Optional[list[OffreOut]]

    class Config:    
        from_attributes = True

class CompetencesIn(BaseModel):
    nom_competence: str = Field(min_length= 5, max_length= 15, pattern="^[a-zA-Z\s]+$")
    niveau: Optional[str] 

    @field_validator("niveau")
    def valider_niveau(cls, value):
        if value is not None and (len(value) > 15 or len(value) < 5 or not re.match("^[a-zA-Z\s]+$", value)):
            raise ValueError("Le niveau entré est invalide")
        return value

class OffreIn(BaseModel):
    fichier_id: Optional[int]
    nom_entreprise: str = Field(min_length= 2, max_length= 15, pattern="^[a-zA-Z0-9_\-'\s]+$")
    adresse: Optional[str] 
    ville_id_entreprise: Optional[int] 
    titre: str = Field(min_length= 2, max_length= 35, pattern="^[a-zA-Z0-9_'/\"\s]+$")
    teletravail: Optional[str] 
    diplome_requis: Optional[str] 
    niveau_etude_requis: Optional[str] 
    type_offre: Optional[str] 
    annee_experience_min: Optional[int] 
    annee_experience_max: Optional[int] 
    nbr_employes_demande: Optional[int]
    salaire_min: Optional[int]
    salaire_max: Optional[int]
    id_secteur_activite: Optional[int]
    id_fonction: Optional[int]
    description: Optional[str]
    id_ville_offre: Optional[int]
    competences: Optional[list[CompetencesIn]]

    @field_validator("description")
    def valider_desc(cls, value):
        if value is not None and len(value) > 100 :
            raise ValueError("La description ne doit pas dépasser 100 caractères")
        return value
    
    @field_validator("adresse")
    def valider_adr(cls, value):
        if value is not None and len(value) > 50 :
            raise ValueError("L'adresse ne doit pas dépasser 50 caractères")
        return value

class CompetencesUpdate(BaseModel):
    nom_competence: Optional[str] = Field(None, min_length=5, max_length=15, pattern="^[a-zA-Z\s]+$") 
    niveau: Optional[str] = Field(None, min_length=5, max_length=15, pattern="^[a-zA-Z\s]+$") 

class EntrepriseUpdate(BaseModel):
    nom_entreprise: Optional[str] = Field(None, min_length=2, max_length=15, pattern="^[a-zA-Z0-9_\-'\s]+$") 
    adresse: Optional[str] = Field(None, max_length=50) 
    ville_id: Optional[int] = None

class OffreUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=2, max_length=15, pattern="^[a-zA-Z0-9_'/\"\s]+$") 
    teletravail: Optional[str] = None
    diplome_requis: Optional[str] = None
    niveau_etude_requis: Optional[str] = None
    type_offre: Optional[str] = None
    annees_experience_min: Optional[int] = None
    annees_experience_max: Optional[int] = None
    nbr_employes_demande: Optional[int] = None
    salaire_min: Optional[int] = None
    salaire_max: Optional[int] = None
    secteur_activite_id: Optional[int] = None
    fonction_id: Optional[int] = None
    description: Optional[str] = None
    ville_id: Optional[int] = None
    entreprise: Optional[EntrepriseUpdate] = None
    competences: Optional[list[CompetencesUpdate]] = None

class ApplyIn(BaseModel):
    cv_id: Optional[int]
    nom: str = Field(min_length= 3, max_length= 10, pattern="^[a-zA-Z\-\s]+$")
    prenom: str = Field(min_length= 3, max_length= 10, pattern="^[a-zA-Z\-\s]+$")
    email: Optional[EmailStr]
    numero_tel: str = Field(..., min_length=10, max_length=10, pattern=r"^(05|06|07)\d{8}$")