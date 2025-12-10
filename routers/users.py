from typing import Any
from fastapi import Depends, HTTPException
from sqlalchemy import select  # noqa: F401
from database import get_db
from schemas.models import User
from schemas.schemas import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
)
from sqlalchemy.orm import Session
from utility.oauth2 import (
    create_access_token,
    get_current_user,
)  # noqa: F401
from utility.hash import hash_password, verify_password  # noqa: F401
from fastapi import APIRouter


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signin", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password: str = hash_password(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", status_code=200, response_model=Token)
def login_user(
    user: LoginRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user_data: User | None = db.scalar(
        select(User).where(User.email == user.email)
    )
    if not user_data:
        raise HTTPException(
            status_code=403,
            detail="Unknown user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if verify_password(user.password, user_data.password) is False:
        raise HTTPException(
            status_code=403,
            detail="Unknown user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token: str = create_access_token(
        data={"user_id": user_data.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# test function for jwt
@router.get("/protected", response_model=UserResponse)
def protected_route(
    current_user: UserResponse = Depends(get_current_user),
):
    response: dict[str, Any] = {
        "id": current_user.id,
        "email": current_user.email,
    }
    return response


@router.get("/{id}", status_code=200, response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)) -> User:
    user: UserResponse = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
