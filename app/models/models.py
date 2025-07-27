from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from database.database import Base


gmt_plus_1_timezone = timezone(timedelta(hours=1))

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key = True, autoincrement = True)
    role_name = Column(String, unique = True, nullable = False)

    users = relationship("User", back_populates = "role")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(gmt_plus_1_timezone))
    updated_at = Column(DateTime, nullable=True)

    role = relationship("Role", back_populates="users")
    offres_emploi = relationship("OffreEmploi", back_populates = "user")

class OffreEmploi(Base):
    __tablename__ = "offres_emploi"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    titre = Column(String, nullable=False)
    entreprise_id = Column(Integer ,ForeignKey("entreprises.id"), unique=True, nullable = False)
    teletravail = Column(String, nullable=False)
    ville_id = Column(Integer ,ForeignKey("villes.id"), nullable=False)
    secteur_activite_id = Column(Integer ,ForeignKey("secteurs_activite.id"), nullable=False)
    fonction_id = Column(Integer ,ForeignKey("fonctions.id"), nullable=False)
    diplome_requis = Column(String)
    niveau_etude_requis = Column(String)
    type_offre = Column(String, nullable=False)
    annees_experience_min = Column(Integer)
    annees_experience_max = Column(Integer)
    nbr_employes_demande = Column(Integer, nullable=False)
    salaire_min  = Column(Integer)
    salaire_max = Column(Integer)
    description = Column(Text)
    nbr_candidats = Column(Integer, default = 0 )
    created_at = Column(DateTime, default = datetime.now(gmt_plus_1_timezone))
    updated_at = Column(DateTime)

    user = relationship("User", back_populates = "offres_emploi")
    entreprise = relationship("Entreprise", back_populates = "offre")
    ville = relationship("Ville", back_populates = "offres_emploi")
    secteur_activite = relationship("SecteurActivite", back_populates = "offres_emploi")
    fonction = relationship("Fonction", back_populates = "offres_emploi")
    competences = relationship("Competence", back_populates = "offre")
    candidatures = relationship("Candidature", back_populates = "offre")

class Entreprise(Base):
    __tablename__ = "entreprises"

    id = Column(Integer, primary_key = True, autoincrement=True)
    nom_entreprise = Column(String, nullable = False)
    logo_id = Column(Integer, ForeignKey(("files.id")),nullable = False)
    ville_id = Column(Integer, ForeignKey(("villes.id")), nullable = False)
    adresse = Column(Text)

    offre = relationship("OffreEmploi", back_populates = "entreprise") 
    logo = relationship("File", back_populates = "entreprise")
    ville = relationship("Ville", back_populates = "entreprises")

class Ville(Base):
    __tablename__ = "villes"

    id = Column(Integer, primary_key = True, autoincrement = True)
    nom_ville = Column(String, nullable = False, unique=True)

    offres_emploi = relationship("OffreEmploi", back_populates = "ville")
    entreprises = relationship("Entreprise", back_populates = "ville")

class File(Base):
    __tablename__ = "files"

    id =Column(Integer, primary_key = True, autoincrement = True)
    file_path = Column(String, nullable = False, unique=True)
    file_name = Column(String, nullable = False, unique=True)
    file_type = Column(String, nullable = False)

    candidature = relationship("Candidature", back_populates = "cv")
    entreprise = relationship("Entreprise", back_populates = "logo") 

class Competence(Base): 
    __tablename__ = "competences"

    id = Column(Integer, primary_key = True, autoincrement = True)
    nom_competence = Column(String, nullable=False)
    niveau = Column(String)
    id_offre = Column(Integer, ForeignKey(("offres_emploi.id")), nullable=False)
    
    offre = relationship("OffreEmploi", back_populates = "competences")

class Fonction(Base):
    __tablename__ = "fonctions"

    id = Column(Integer, primary_key = True, autoincrement = True)
    nom_fonction = Column(String, nullable=False, unique=True)

    offres_emploi = relationship("OffreEmploi", back_populates = "fonction")

class SecteurActivite(Base):
    __tablename__ = "secteurs_activite"

    id = Column(Integer, primary_key = True, autoincrement = True)
    nom_secteur = Column(String, nullable=False, unique=True)

    offres_emploi = relationship("OffreEmploi", back_populates = "secteur_activite")

class Candidature(Base):
    __tablename__ = "candidatures"

    id = Column(Integer, primary_key = True, autoincrement = True)
    id_offre = Column(Integer, ForeignKey(("offres_emploi.id")), nullable=False)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, nullable=False)
    numero_tel = Column(String, nullable=False)
    cv_id = Column(Integer, ForeignKey(("files.id")), nullable=False, unique=True)
    date_postulation = Column(DateTime, default = datetime.now(gmt_plus_1_timezone))

    offre = relationship("OffreEmploi", back_populates = "candidatures")
    cv = relationship("File", back_populates = "candidature")