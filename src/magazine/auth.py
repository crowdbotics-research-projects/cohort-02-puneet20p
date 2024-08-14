from jose import JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User
from db import get_db

# Secret key for enconding JWT token
SECRET_KEY = "user-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(datetime.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_token(db: Session, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
            raise HTTPException(status_code=401, detail="Token has expired")
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    return user


def get_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user = get_user_by_token(db, token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid Token")

    except KeyError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    except Exception as e:
        print("Got exception", e)
        raise

    return user
