# path fix to be able to run seed script
import sys
import os

from sqlalchemy import select

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from typing import Sequence  # noqa: E402
from database import engine  # noqa: E402
from schemas.models import WorkoutPlans, User  # noqa: E402
from schemas.schemas import WorkoutPlanCreate  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

workout_plans = [
    {
        "user_id": 1,
        "title": "full body",
        "description": "full body training",
        "is_public": True,
    },
    {
        "user_id": 2,
        "title": "push day",
        "description": "training of the push zones",
        "is_public": False,
    },
    {
        "user_id": 3,
        "title": "pull day",
        "description": "training of the pull zones",
        "is_public": True,
    },
    {
        "user_id": 4,
        "title": "leg day",
        "description": "training of leg zones",
        "is_public": False,
    },
    {
        "user_id": 1,
        "title": "abs & core routine",
        "description": "",
        "is_public": False,
    },
    {
        "user_id": 2,
        "title": "home no-equipment workout",
        "description": "no equipment plan",
        "is_public": True,
    },
    {
        "user_id": 3,
        "title": "strength build",
        "description": "strength progress training",
        "is_public": False,
    },
    {
        "user_id": 4,
        "title": "fat burner",
        "description": "short intensive intervals for the fatburning",
    },
]


def create_workout_plan(plans: list):
    Session = sessionmaker(bind=engine)
    session = Session()
    with session.begin():
        get_users_id: Sequence[int] = (
            session.execute(select(User.id)).scalars().all()
        )
    try:
        for plan in plans:
            if not plan.get("is_public"):
                plan["is_public"] = False
            if not plan.get("description"):
                plan["description"] = ""
            is_valid: WorkoutPlanCreate = WorkoutPlanCreate(
                user_id=plan["user_id"],
                title=plan["title"],
                description=plan["description"],
                is_public=plan["is_public"],
            )
            if is_valid.user_id not in get_users_id:
                raise ValueError(
                    f"User with id {is_valid.user_id} doesnt exists"
                )
            get_plans: dict = (
                session.query(WorkoutPlans)
                .filter(
                    WorkoutPlans.description == is_valid.description,
                    WorkoutPlans.title == is_valid.title,
                )
                .first()
            )
            if not get_plans:
                new_plan: WorkoutPlanCreate = WorkoutPlans(
                    user_id=is_valid.user_id,
                    title=is_valid.title,
                    description=is_valid.description,
                    is_public=is_valid.is_public,
                )
                session.add(new_plan)
                session.commit()
    except Exception as e:
        raise e
    finally:
        session.close()


create_workout_plan(workout_plans)
