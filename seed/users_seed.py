# path fix to be able to run seed script
import sys
import os

from pydantic import ValidationError


sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# imports won't work otherwise, sys.path initialize has to be ontop of the file
from database import engine  # noqa: E402 # noqa: E402
from schemas.models import User  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from utility import hash  # noqa: E402
from schemas.schemas import UserCreate  # noqa: E402


users: dict = {
    "user@example.com": "12345678",
    "johndoe@example.com": "12345678",
    "janedoe@example.com": "password",
    "immark@example.com": "mycoolpassword",
    "kol": 1234,
}


def create_users(users: dict):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for email, password in users.items():

            is_valid: UserCreate = UserCreate(
                email=email, password=password
            )
            existing_user: dict = (
                session.query(User)
                .filter(User.email == email)
                .first()
            )
            if not existing_user:
                new_user: UserCreate = User(
                    email=is_valid.email,
                    password=hash.hash_password(is_valid.password),
                )
                session.add(new_user)
                session.commit()
            else:
                continue
    except ValidationError as exc:
        print(exc)
    finally:
        session.close()


create_users(users)
