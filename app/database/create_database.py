import sqlite3
import pathlib
import os

DB_PATH = os.path.join(pathlib.Path(__file__).parent.parent.parent, 'database.sqlite')

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(role_id) REFERENCES roles(id)
)
""")

cursor.execute("""
CREATE TABLE villes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_ville TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT UNIQUE NOT NULL,
    file_type TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE entreprises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_entreprise TEXT NOT NULL,
    logo_id INTEGER NOT NULL,
    ville_id INTEGER NOT NULL,
    adresse TEXT,
    FOREIGN KEY(logo_id) REFERENCES files(id),
    FOREIGN KEY(ville_id) REFERENCES villes(id)
)
""")

cursor.execute("""
CREATE TABLE secteurs_activite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_secteur TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE fonctions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fonction TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE offres_emploi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    titre TEXT NOT NULL,
    entreprise_id INTEGER UNIQUE NOT NULL,
    teletravail TEXT NOT NULL,
    ville_id INTEGER NOT NULL,
    secteur_activite_id INTEGER NOT NULL,
    fonction_id INTEGER NOT NULL,
    diplome_requis TEXT,
    niveau_etude_requis TEXT,
    type_offre TEXT NOT NULL,
    annees_experience_min INTEGER,
    annees_experience_max INTEGER,
    nbr_employes_demande INTEGER NOT NULL,
    salaire_min INTEGER,
    salaire_max INTEGER,
    description TEXT,
    nbr_candidats INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(entreprise_id) REFERENCES entreprises(id),
    FOREIGN KEY(ville_id) REFERENCES villes(id),
    FOREIGN KEY(secteur_activite_id) REFERENCES secteurs_activite(id),
    FOREIGN KEY(fonction_id) REFERENCES fonctions(id)
)
""")

cursor.execute("""
CREATE TABLE competences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_competence TEXT NOT NULL,
    niveau TEXT,
    id_offre INTEGER NOT NULL,
    FOREIGN KEY(id_offre) REFERENCES offres_emploi(id)
)
""")

cursor.execute("""
CREATE TABLE candidatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_offre INTEGER NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    numero_tel TEXT NOT NULL,
    cv_id INTEGER UNIQUE NOT NULL,
    date_postulation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_offre) REFERENCES offres_emploi(id),
    FOREIGN KEY(cv_id) REFERENCES files(id)
)
""")

placeholder_path = os.path.join(pathlib.Path(__file__).parent.parent.parent, 'placeholder.png' )

cursor.execute("INSERT INTO files VALUES (?, ?, ?, ?) ", (1, placeholder_path, "placeholder.png", "image/png"))

conn.commit()
conn.close()