# path fix to be able to run seed script
import sys
import os
from typing import Sequence

from sqlalchemy import select  # noqa: F401

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# imports won't work otherwise, sys.path initialize has to be ontop of the file
from database import engine  # noqa: E402 # noqa: E402
from schemas.models import Exercise, ExerciseCategory  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from schemas.schemas import (  # noqa: E402
    ExerciseS,
)  # noqa: E402


exercise = [
    {
        "name": "swimming",
        "description": "Swimming is amazing for cardio",
        "category_id": 3,
    },
    {
        "name": "walking lunges",
        "description": "Step forward with your right foot, lunging with your\n"
        " right leg until your thigh is parallel to the ground",
        "category_id": 1,
    },
    {
        "name": "pull-down",
        "description": "The lat pulldown mimics the motion of a pull-up,\n"
        " making it a great choice for those looking to target their lats\n"
        " and/or work toward a bodyweight pull-up ",
        "category_id": 4,
    },
    {
        "name": "pushups",
        "description": "The classic pushup is one of the easiest chest\n"
        "workouts you can do indoors – or outdoors!",
        "category_id": 5,
    },
    {
        "name": "ez-bar curl",
        "description": " The EZ bar is probably not the first piece of\n"
        " equipment you'd go for if we asked you to do bicep curls",
        "category_id": 2,
    },
    {
        "name": "upright row",
        "description": "The upright row is a versatile shoulder exercise\n"
        " that targets the delts and trapezius. ",
        "category_id": 6,
    },
    {
        "name": "cable crunch",
        "description": " If there's one exercise you shouldn't skip in\n"
        " your next ab workout, it's the kneeling cable crunch.",
        "category_id": 7,
    },
]


def create_exercise(exercises: list):
    Session = sessionmaker(bind=engine)
    session = Session()
    with session:
        exercise_types_id: Sequence[int] = (
            session.execute(select(ExerciseCategory.id))
            .scalars()
            .all()
        )
    try:
        for exercise in exercises:
            is_valid: ExerciseS = ExerciseS(
                name=exercise["name"],
                description=exercise["description"],
                category_id=exercise["category_id"],
            )
            if is_valid.category_id not in exercise_types_id:
                raise ValueError(f"{is_valid.category_id} not found")
            get_exercise_name: dict = (
                session.query(Exercise)
                .filter(Exercise.name == exercise["name"])
                .first()
            )

            if not get_exercise_name:
                new_exercise: ExerciseCategory = Exercise(
                    name=is_valid.name,
                    description=is_valid.description,
                    category_id=is_valid.category_id,
                )
                session.add(new_exercise)
                session.commit()
            else:
                continue
    except Exception as e:
        print(e)
    finally:
        session.close()


create_exercise(exercise)
