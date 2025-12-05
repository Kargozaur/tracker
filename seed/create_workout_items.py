# path fix to be able to run seed script
import sys
import os
from typing import Sequence


sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from database import engine  # noqa: E402
from schemas.models import (  # noqa: E402
    Exercise,
    WorkoutItems,
    WorkoutPlans,
)
from schemas.schemas import WorkoutItemsS  # noqa: E402

workout_items = [
    {
        "plan_id": 1,
        "exercise_id": 1,  # swimming
        "sets": 1,
        "reps": "10 min",
        "weight": 0.0,
        "rest_seconds": 0,
    },
    {
        "plan_id": 1,
        "exercise_id": 2,  # walking lunges
        "sets": 3,
        "reps": "20 steps",
        "weight": 0.0,
        "rest_seconds": 60,
    },
    {
        "plan_id": 1,
        "exercise_id": 4,  # pushups
        "sets": 3,
        "reps": "12",
        "weight": 0.0,
        "rest_seconds": 60,
    },
    {
        "plan_id": 2,
        "exercise_id": 4,  # pushups
        "sets": 4,
        "reps": "15",
        "weight": 0.0,
        "rest_seconds": 90,
    },
    {
        "plan_id": 2,
        "exercise_id": 6,  # upright row
        "sets": 3,
        "reps": "10",
        "weight": 20.0,
        "rest_seconds": 90,
    },
    {
        "plan_id": 3,
        "exercise_id": 3,  # pull-down
        "sets": 4,
        "reps": "12",
        "weight": 35.0,
        "rest_seconds": 90,
    },
    {
        "plan_id": 3,
        "exercise_id": 5,  # ez-bar curl
        "sets": 3,
        "reps": "10–12",
        "weight": 15.0,
        "rest_seconds": 60,
    },
    {
        "plan_id": 4,
        "exercise_id": 2,  # walking lunges
        "sets": 4,
        "reps": "20 steps",
        "weight": 0.0,
        "rest_seconds": 60,
    },
    {
        "plan_id": 5,
        "exercise_id": 7,  # cable crunch
        "sets": 4,
        "reps": "15",
        "weight": 20.0,
        "rest_seconds": 60,
    },
    {
        "plan_id": 5,
        "exercise_id": 4,  # pushups (used as plank-like core)
        "sets": 3,
        "reps": "20",
        "weight": 0.0,
        "rest_seconds": 45,
    },
    {
        "plan_id": 6,
        "exercise_id": 4,  # pushups
        "sets": 4,
        "reps": "12–15",
        "weight": 0.0,
        "rest_seconds": 60,
    },
    {
        "plan_id": 6,
        "exercise_id": 2,  # walking lunges
        "sets": 3,
        "reps": "20 steps",
        "weight": 0.0,
        "rest_seconds": 45,
    },
    {
        "plan_id": 7,
        "exercise_id": 6,  # upright row
        "sets": 5,
        "reps": "8",
        "weight": 25.0,
        "rest_seconds": 120,
    },
    {
        "plan_id": 7,
        "exercise_id": 5,  # ez-bar curl
        "sets": 4,
        "reps": "10",
        "weight": 20.0,
        "rest_seconds": 90,
    },
    {
        "plan_id": 8,
        "exercise_id": 1,  # swimming
        "sets": 1,
        "reps": "15 min",
        "weight": 0.0,
        "rest_seconds": 0,
    },
    {
        "plan_id": 8,
        "exercise_id": 2,  # walking lunges
        "sets": 4,
        "reps": "20 steps",
        "weight": 0.0,
        "rest_seconds": 45,
    },
    {
        "plan_id": 8,
        "exercise_id": 4,  # pushups
        "sets": 3,
        "reps": "15",
        "weight": 0.0,
        "rest_seconds": 45,
    },
]


def create_workout_items(items: list):
    Session = sessionmaker(bind=engine)
    session = Session()
    with session:
        p_id: Sequence[int] = (
            session.execute(select(WorkoutPlans.id)).scalars().all()
        )
        e_id: Sequence[int] = (
            session.execute(select(Exercise.id)).scalars().all()
        )
    try:
        for item in items:
            is_valid: WorkoutItemsS = WorkoutItemsS(
                plan_id=item["plan_id"],
                exercise_id=item["exercise_id"],
                sets=item["sets"],
                reps=item["reps"],
                weight=item["weight"],
                rest_seconds=item["rest_seconds"],
            )
            if is_valid.plan_id not in p_id:
                raise ValueError(
                    f"Plan with id {is_valid.plan_id} doesnt exists"
                )
            if is_valid.exercise_id not in e_id:
                raise ValueError(
                    f"Exercise with id {is_valid.exercise_id} doesnt exists"
                )
            get_items = (
                session.query(WorkoutItems)
                .filter(
                    WorkoutItems.exercise_id == is_valid.exercise_id,
                    WorkoutItems.plan_id == is_valid.plan_id,
                )
                .first()
            )
            if not get_items:
                new_items = WorkoutItems(
                    plan_id=is_valid.plan_id,
                    exercise_id=is_valid.exercise_id,
                    sets=is_valid.sets,
                    reps=is_valid.reps,
                    weight=is_valid.weight,
                    rest_seconds=is_valid.rest_seconds,
                )
                session.add(new_items)
                session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


create_workout_items(workout_items)
