from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from schemas import models
from schemas.schemas import TokenData

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


def create_access_token(data: dict) -> str:
    to_encode: dict = data.copy()
    expire: datetime = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def verify_access_token(token: str, credential_exception) -> str:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str | None = payload.get("user_id")
        if not id:
            raise credential_exception
        token_data: str = TokenData(id=id)
    except JWTError:
        raise credential_exception
    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> dict:
    credential_exception = HTTPException(
        status_code=401, detail="Unathorized", headers={"WWW-Authenticate": "Bearer"}
    )
    token: str = verify_access_token(token, credential_exception)
    user: dict = db.query(models.User).filter(models.User.id == token.id).first()
    return user
