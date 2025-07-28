from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from models.models import User, OffreEmploi
from database.database import get_db
from typing import Annotated
from shemas.user import UserIn, UserOut, UserUpdate
from services.user import check_user_exist, create_and_save_user, get_current_user, hash_password, delete_candidatures, delete_competences, delete_entreprise, delete_resource, update_user, add_jwt_token_to_revoked_tokens
from fastapi import APIRouter
from services.auth import oauth2_scheme

router = APIRouter(tags=["users"])

@router.get("/users/moi", response_model=UserOut)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.post("/users", status_code = 201)
def inscription(user: UserIn, db: Session = Depends(get_db)):
    if check_user_exist(user.email, db):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    u = create_and_save_user(user.first_name, user.last_name, user.email, user.password, db)
    return {"message": "user " + str(u.id) + " crée"}

@router.patch("/users")
def modifer_compte(current_user: Annotated[User, Depends(get_current_user)], user: UserUpdate, db: Session = Depends(get_db)):
    update_data = user.model_dump(exclude_unset=True)
    if "email" in update_data and check_user_exist(update_data["email"], db):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if "password_hash" in update_data:
        update_data["password_hash"] = hash_password(update_data["password_hash"])
    update_user(update_data, current_user, db)
    return {"message": "Compte mis à jour", "id_user": current_user.id}

@router.delete("/users")
def delete_user_by_id(current_user: Annotated[User, Depends(get_current_user)], token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    offres = db.query(OffreEmploi).filter(OffreEmploi.user_id == current_user.id)
    for offre in offres:
        delete_competences(offre, db)
        delete_candidatures(offre, db)
        delete_entreprise(offre, db)
        delete_resource(offre, db)
    add_jwt_token_to_revoked_tokens(token, db)
    delete_resource(current_user,db)
    return {"message": "user_supprimé"}

@router.delete("/users/deconnexion")
def add_jwt_to_revoked_tokens(current_user: Annotated[User, Depends(get_current_user)], token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    add_jwt_token_to_revoked_tokens(token, db)
    return {"message": "déconnexion reussie"}