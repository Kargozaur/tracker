from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
from schemas.models import Exercise, ExerciseCategory
from schemas.schemas import (
    ExerciseResponse,
)
from fastapi import APIRouter

from utility.oauth2 import get_current_user

router = APIRouter(prefix="/exercise", tags=["exercises"])


@router.get("/", response_model=List[ExerciseResponse])
def get_all_exercises(
    db: Session = Depends(get_db),
):
    exercises = (
        db.execute(
            (
                select(
                    ExerciseCategory.name.label("category"),
                    Exercise.name.label("title"),
                    Exercise.description,
                )
                .join(ExerciseCategory.exercises)
                .where(Exercise.is_global.is_(True))
            )
        )
        .mappings()
        .all()
    )
    if not exercises:
        raise HTTPException(
            status_code=404, detail="Exercises are not found"
        )
    return exercises


@router.get(
    "/{id}",
    response_model=List[ExerciseResponse],
)
def get_exercise_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = (
        select(
            ExerciseCategory.name.label("category"),
            Exercise.name.label("title"),
            Exercise.description,
        )
        .join(ExerciseCategory.exercises)
        .where(Exercise.id == id)
    )
    if current_user:
        query = query.where(
            Exercise.is_global.is_(True)
            | (Exercise.owner_id == current_user.id)
        )
    exercises = db.execute(query).mappings().all()
    if not exercises:
        raise HTTPException(
            status_code=403, detail="Exercise is not found"
        )

    return exercises
