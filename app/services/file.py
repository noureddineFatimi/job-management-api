import models.models
from models.models import Entreprise
import random
import string
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import Depends, UploadFile, HTTPException
from database.database import get_db

UPLOAD_PATH = Path(__file__).resolve().parent.parent.parent / "uploads"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
ALLOWED_DOC_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE = 5 * 1024 * 1024 

def check_file_exist(id_file:int, db: Session = Depends(get_db)):
    return db.query(models.models.File).get(id_file)

def check_file__type_allowed(content_type, allowed_type):
    return content_type not in allowed_type

def check_file_size_allowed(content, size_allowed):
    return len(content) > size_allowed

def upload_file(file, content, content_type, upload_folder):
    extension = Path(file.filename).suffix.lower()
    upload_folder.mkdir(parents=True, exist_ok=True)
    secure_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15)) + extension
    full_path = upload_folder / secure_name
    with open(full_path, "wb") as f:
        f.write(content)
    fichier = models.models.File(
        file_name=secure_name,
        file_type=content_type,
        file_path=str(full_path)
    )
    return fichier

def save_file(fichier,  db: Session = Depends(get_db)):
    db.add(fichier)
    db.commit()
    db.refresh(fichier)
    return fichier

def check_entreprise_exist(id_entreprise:str, db: Session = Depends(get_db)):
    return db.query(Entreprise).get(id_entreprise)

def update_logo(entreprise, fichier, db: Session = Depends(get_db)):
    if entreprise.logo_id != 1 :
        Path(entreprise.logo.file_path).unlink()
        logo_deleted = entreprise.logo
        entreprise.logo_id = fichier.id
        db.commit()
        db.delete(logo_deleted)
        db.commit()
    else:
        entreprise.logo_id = fichier.id
    db.commit()
    db.refresh(entreprise)
    return entreprise

def delete_logo(entreprise,  db: Session = Depends(get_db)):
    message = { "message": "rien à supprimer"}
    if entreprise.logo_id != 1:
        Path(entreprise.logo.file_path).unlink()
        logo_deleted = entreprise.logo
        entreprise.logo_id = 1
        db.commit()
        db.delete(logo_deleted)
        db.commit()
        message = {"message": "image_supprimé"}
    return message

async def process_upload_file(file: UploadFile, allowed_types: set[str], max_size: int, upload_folder: Path, db):
    content_type = file.content_type
    if check_file__type_allowed(content_type, allowed_types):
        raise HTTPException(status_code=400, detail="Type de fichier non supporté")
    content = await file.read()
    if check_file_size_allowed(content, max_size):
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 5 Mo)")
    fichier = upload_file(file, content, content_type, upload_folder)
    fichier = save_file(fichier, db)
    return fichier