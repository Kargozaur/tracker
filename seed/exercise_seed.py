# path fix to be able to run seed script
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# imports won't work otherwise, sys.path initialize has to be ontop of the file
from database import engine  # noqa: E402
from schemas.models import ExerciseCategory  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402


exercise_category: list = [
    "legs",
    "biceps",
    "cardio",
    "back",
    "chest",
    "shoulders",
    "abs",
]


def add_values(values: list):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.begin()
    for value in values:
        existing_category: dict = (
            session.query(ExerciseCategory)
            .filter(ExerciseCategory.name == value)
            .first()
        )
        if existing_category:
            continue
        else:
            new_exercise_type = ExerciseCategory(name=value)
            session.add(new_exercise_type)
            session.commit()

    session.close()


add_values(exercise_category)
