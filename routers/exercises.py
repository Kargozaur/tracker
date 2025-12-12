from typing import Annotated, List, Optional, Sequence
from fastapi import Depends, HTTPException, Query, Response
from sqlalchemy import RowMapping, select
from sqlalchemy.orm import Session
from database import get_db
from schemas.models import Exercise, ExerciseCategory
from schemas.schemas import (
    ExerciseCreateResponse,
    ExerciseResponse,
    ExerciseUpdate,
    ExercisesCreate,
    PaginationParams,
)
from fastapi import APIRouter

from utility.oauth2 import get_current_user, get_optional_user

router = APIRouter(prefix="/exercise", tags=["exercises"])

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


@router.get("/", response_model=List[ExerciseResponse])
def get_all_exercises_for_user(
    pagination: PaginationDep,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
    search: Optional[str] = Query(default="", alias="name"),
):
    query = select(
        ExerciseCategory.name.label("category"),
        Exercise.name.label("title"),
        Exercise.description,
    ).join(ExerciseCategory.exercises)
    if not current_user:
        query = query.where(
            Exercise.name.contains(search),
            (Exercise.is_global.is_(True)),
        )
    elif current_user:
        query = query.where(
            Exercise.name.contains(search),
            (Exercise.is_global.is_(True))
            | (Exercise.owner_id == current_user.id),
        )
    query = query.limit(pagination.limit).offset(pagination.offset)
    exercises: Sequence[RowMapping] = (
        db.execute(query).mappings().all()
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
    current_user=Depends(get_optional_user),
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
    exercises: Sequence[RowMapping] = (
        db.execute(query).mappings().all()
    )
    if not exercises:
        raise HTTPException(
            status_code=404, detail="Exercise is not found"
        )

    return exercises


@router.post(
    "/create_exercise", response_model=ExerciseCreateResponse
)
def create_exercise(
    exercise: ExercisesCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    exercise_exists: RowMapping | None = (
        db.execute(
            select(Exercise.name, Exercise.description).where(
                Exercise.name == exercise.name,
                Exercise.description == exercise.description,
            )
        )
        .mappings()
        .first()
    )
    if exercise_exists:
        raise HTTPException(
            status_code=409, detail="Exercise already exists"
        )
    new_exercise: Exercise = Exercise(
        owner_id=current_user.id, **exercise.model_dump()
    )
    try:
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=422, detail="wrong credentials"
        )

    return new_exercise


@router.delete("/{id}", status_code=204)
def delete_exercise(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    delete_exercise: Exercise | None = db.execute(
        select(Exercise).where(Exercise.id == id)
    ).scalar_one_or_none()
    if not delete_exercise:
        raise HTTPException(
            status_code=404, detail="Exercise not found"
        )

    if delete_exercise.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        db.delete(delete_exercise)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.put("/{id}", status_code=205)
def update_exercise(
    id: int,
    exercise: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    update_exercise: Exercise | None = db.execute(
        select(Exercise).where(Exercise.id == id)
    ).scalar_one_or_none()

    if not update_exercise:
        raise HTTPException(
            status_code=404, detail="Exercise not found"
        )
    if update_exercise.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unathorized")

    update_data = exercise.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(update_exercise, field, value)
    db.commit()
    db.refresh(update_exercise)
    return Response(status_code=205)
