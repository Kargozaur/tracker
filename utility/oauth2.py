from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from schemas import models
from schemas.schemas import TokenData
from settings import settings
from typing import Any

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict) -> str:
    to_encode: dict = data.copy()
    expire: datetime | float = datetime.now() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded: str = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded


def verify_access_token(token: str, credential_exception) -> dict:
    try:
        payload: dict = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        id = payload.get("user_id")
        if not id:
            raise credential_exception
        token_data: Any = TokenData(id=id)
    except JWTError:
        raise credential_exception
    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> dict:
    credential_exception = HTTPException(
        status_code=401,
        detail="Unathorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_d: dict = verify_access_token(token, credential_exception)
    user: dict = (
        db.query(models.User)
        .filter(models.User.id == token_d.id)
        .first()
    )
    return user
