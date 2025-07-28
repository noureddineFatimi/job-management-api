from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from database.database import get_db
from fastapi import APIRouter
from typing import Optional
from routers.user import get_current_user 
from typing import Annotated
from services.file import ALLOWED_IMAGE_TYPES, process_upload_file, check_file_exist, UPLOAD_PATH, check_entreprise_exist, delete_logo, MAX_FILE_SIZE, ALLOWED_DOC_TYPES, update_logo
from models.models import User

router = APIRouter(tags=["fichiers"])

@router.get("/fichiers/{id_fichier}")
def recuperer_fichier_par_id(id_file: int, db: Session = Depends(get_db)):
    file = check_file_exist(id_file, db)
    if not file:
        raise HTTPException(status_code = 404, detail = "fichier_inexistant")
    return FileResponse(path = file.file_path, media_type = file.file_type, filename = file.file_name)

@router.post("/entreprises/logo", status_code= 201)
async def ajouter_logo_entreprise(current_user: Annotated[User, Depends(get_current_user)], file: Optional[UploadFile] = File(None), db: Session = Depends(get_db)):
    if file is None: 
        return {"id_fichier": 1}
    fichier = await process_upload_file(file=file, allowed_types=ALLOWED_IMAGE_TYPES, max_size=MAX_FILE_SIZE, upload_folder=UPLOAD_PATH / "images", db = db)
    return {"id_fichier": fichier.id}

@router.post("/candidats/cv", status_code = 201)
async def ajouter_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    fichier = await process_upload_file(file=file, allowed_types=ALLOWED_DOC_TYPES, max_size=MAX_FILE_SIZE, upload_folder=UPLOAD_PATH / "cv", db=db)
    return {"id_fichier": fichier.id}

@router.patch("/entreprises/{id_entreprise}/logo")
async def modifier_logo_entreprise(current_user: Annotated[User, Depends(get_current_user)], id_entreprise: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    e = check_entreprise_exist(id_entreprise, db)
    if not e:
        raise HTTPException(status_code=404, detail="entreprise_inexistant")
    fichier = await process_upload_file(file=file, allowed_types=ALLOWED_IMAGE_TYPES, max_size=MAX_FILE_SIZE, upload_folder=UPLOAD_PATH / "images", db=db)
    e = update_logo(e, fichier, db)
    return {"message": "success", "entreprise_logo_id": e.logo_id}

@router.delete("/entreprises/{id_entreprise}/logo")
def supprimer_logo_entreprise(current_user: Annotated[User, Depends(get_current_user)], id_entreprise: int, db: Session = Depends(get_db)):
    e = check_entreprise_exist(id_entreprise, db)
    if not e:
        raise HTTPException(status_code = 404, detail = "entreprise_inexistant")
    m = delete_logo(e, db)
    return m