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
CREATE TABLE revoked_tokens(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jti TEXT UNIQUE NOT NULL,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    deadline_postulation TIMESTAMP NOT NULL,
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

fonctions = [
    "Achats / Supply Chain",
    "Administration des ventes / SAV",
    "Agriculture (métiers de l')",
    "Assistanat de Direction / Services Généraux",
    "Assurance (métiers de l')",
    "Audit / Conseil",
    "Avocat / Juriste / Fiscaliste",
    "Banque (métiers de la)",
    "Call Centers (métiers de)",
    "Caméraman / Monteur / Preneur de son",
    "Commercial / Vente / Export",
    "Communication / Publicité / RP",
    "Coursier / Gardiennage / Propreté",
    "Dirigeants sur ExeKutive.biz",
    "Distribution (métiers de la)",
    "Electricité",
    "Enseignement",
    "Environnement (métiers de l')",
    "Gestion / Comptabilité / Finance",
    "Gestion projet / Etudes / R&D",
    "Hôtellerie / Restauration (métiers de)",
    "Immobilier / Promotion (métiers de)",
    "Informatique / Electronique",
    "Journalisme / Traduction",
    "Logistique / Transport (métiers de)",
    "Marketing",
    "Multimédia / Internet",
    "Médical / Paramédical",
    "Méthodes / Process / Industrialisation",
    "Production / Qualité / Sécurité / Maintenance",
    "RH / Personnel / Formation",
    "Responsable de Département",
    "Santé / Social (métiers de)",
    "Sport / Loisirs (métiers de)",
    "Tourisme (métiers du)",
    "Travaux / Chantiers / BTP",
    "Télécoms / Réseaux",
    "Urbanisme / architecture"
]

for nom in fonctions:
    cursor.execute("INSERT INTO fonctions (nom_fonction) VALUES (?)", (nom,))

secteurs_activite = [
    "Agence pub / Marketing Direct",
    "Agriculture / Environnement",
    "Agroalimentaire",
    "Ameublement / Décoration",
    "Assurance / Courtage",
    "Audiovisuel",
    "Automobile / Motos / Cycles",
    "Autres Industries",
    "Autres services",
    "Aéronautique / Spatial",
    "BTP / Génie Civil",
    "Banque / Finance",
    "Centre d'appel",
    "Chimie / Parachimie / Peintures",
    "Communication / Evénementiel",
    "Comptabilité / Audit",
    "Conseil / Etudes",
    "Cosmétique / Parfumerie / Luxe",
    "Distribution",
    "Edition / Imprimerie",
    "Electricité",
    "Electro-mécanique / Mécanique",
    "Energie",
    "Enseignement / Formation",
    "Hôtellerie / Restauration",
    "Immobilier / Promoteur / Agence",
    "Import / Export / Négoce",
    "Informatique",
    "Internet / Multimédia",
    "Juridique / Cabinet d’avocats",
    "Métallurgie / Sidérurgie",
    "Offshoring / Nearshoring",
    "Pharmacie / Santé",
    "Plasturgie",
    "Pétrole / Gaz",
    "Recrutement / Intérim",
    "Service public / Administration",
    "Telecom",
    "Textile / Cuir",
    "Tourisme / Voyage / Loisirs",
    "Transport / Messagerie / Logistique"
]

for secteur in secteurs_activite:
    cursor.execute("INSERT INTO secteurs_activite (nom_secteur) VALUES (?)", (secteur,))

villes = [
    "Casablanca", "Fès", "Marrakech", "Tangier", "Sale", "Rabat", "Meknès", "Oujda-Angad", "Kenitra", "Agadir",
    "Tétouan", "Taourirt", "Temara", "Safi", "Khénifra", "El Jadid", "Laâyoune", "Mohammedia", "Kouribga",
    "Béni Mellal", "Ait Melloul", "Nador", "Taza", "Settat", "Barrechid", "Al Khmissat", "Inezgane",
    "Ksar El Kebir", "My Drarga", "Larache", "Guelmim", "Berkane", "Ad Dakhla", "Bouskoura", "Al Fqih Ben Çalah",
    "Oued Zem", "Sidi Slimane", "Errachidia", "Guercif", "Oulad Teïma", "Ben Guerir", "Sefrou", "Fnidq",
    "Sidi Qacem", "Tiznit", "Moulay Abdallah", "Youssoufia", "Martil", "Aïn Harrouda", "Souq Sebt Oulad Nemma",
    "Skhirate", "Ouezzane", "Sidi Yahya Zaer", "Al Hoceïma", "M’diq", "Midalt", "Azrou", "El Kelaa des Srarhna",
    "Ain El Aouda", "Beni Yakhlef", "Ad Darwa", "Al Aaroui", "Qasbat Tadla", "Boujad", "Jerada", "Mrirt",
    "El Aïoun", "Azemmour", "Temsia"
]

for ville in villes:
    cursor.execute("INSERT INTO villes (nom_ville) VALUES (?)", (ville,))

cursor.execute("""
    INSERT INTO roles (role_name) VALUES ("Administrateur")
""")

conn.commit()
conn.close()

print("")
print("Base de données créée avec succès :)")