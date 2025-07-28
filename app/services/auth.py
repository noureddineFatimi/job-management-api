from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, timezone, datetime
from models.models import User
from jwt import encode as jwt_encode
from sqlalchemy.orm import Session
from config import SECRET_KEY, ALGORITHM
from uuid import uuid4

gmt_plus_1_timezone = timezone(timedelta(hours=1))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(email: str, plain_password: str, db: Session) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(plain_password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(gmt_plus_1_timezone) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    encoded_jwt = jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt