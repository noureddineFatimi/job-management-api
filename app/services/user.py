from services.auth import oauth2_scheme, pwd_context
from config import ALGORITHM, SECRET_KEY
from pathlib import Path
from shemas.auth import TokenData
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from jwt import decode
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi import Depends
from typing import Annotated
from models.models import User, Competence, Candidature, OffreEmploi, RevokedToken
import jwt
from config import SECRET_KEY, ALGORITHM
from jose import JWTError

gmt_plus_1_timezone = timezone(timedelta(hours=1))

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if db.query(RevokedToken).filter_by(jti=jti).first():
            raise HTTPException(status_code=401, detail="Token has been revoked")
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(email=token_data.email, db = db)
    if user is None:
        raise credentials_exception
    return user

def check_user_exist(email:str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first() is not None

def create_and_save_user(first_name, last_name, email, password, db: Session = Depends(get_db)):
    u = User(first_name = first_name.lower().capitalize(), last_name = last_name.lower().capitalize(), email = email, password_hash = hash_password(password), role_id = 1)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def update_user(dict, user: User, db: Session = Depends(get_db)):
    for k, v in dict.items():
        setattr(user, k, v)
    user.updated_at = datetime.now(gmt_plus_1_timezone)
    db.commit()
    return user

def delete_competences(offre: OffreEmploi,  db: Session = Depends(get_db)):
    competences = db.query(Competence).filter(Competence.id_offre == offre.id)
    for competence in competences:
        db.delete(competence)

def delete_candidatures(offre: OffreEmploi, db: Session = Depends(get_db)):
    candidatures = db.query(Candidature).filter(Candidature.id_offre == offre.id)
    for candidature in candidatures:
        Path(candidature.cv.file_path).unlink()
        db.delete(candidature.cv)
        db.delete(candidature)

def delete_entreprise(offre: OffreEmploi, db: Session = Depends(get_db)):
    if offre.entreprise.logo_id != 1 :
        Path(offre.entreprise.logo.file_path).unlink()
        db.delete(offre.entreprise.logo)
    db.delete(offre.entreprise)

def delete_resource(ressource, db: Session = Depends(get_db)):
    db.delete(ressource)
    db.commit()

def add_jwt_token_to_revoked_tokens(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            if not db.query(RevokedToken).filter_by(jti=jti).first():
                db.add(RevokedToken(jti=jti))
                db.commit()
    except JWTError:
        raise HTTPException(status_code=400, detail="Erreur lors de la deconnexion : ")