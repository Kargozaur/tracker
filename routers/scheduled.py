from typing import Annotated, List, Sequence
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, RowMapping
from sqlalchemy.orm import Session
from database import get_db
from utility.oauth2 import get_current_user
from schemas.schemas import (
    PaginationParams,
    ScheduleUpdate,
    ScheduledWorkoutCreate,
    ScheduledWorkoutGetResponse,
    ScheduledWorkoutResponse,
)
from schemas.models import ScheduledWorkout, WorkoutPlans

router = APIRouter(prefix="/scheduled", tags=["Scheduled"])
PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


@router.post("/", response_model=ScheduledWorkoutResponse)
def schedule_workout(
    scheduled: ScheduledWorkoutCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_scheduled = ScheduledWorkout(
        user_id=current_user.id, **scheduled.model_dump()
    )

    try:
        db.add(new_scheduled)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.refresh(new_scheduled)

    return new_scheduled


@router.get("/", response_model=List[ScheduledWorkoutGetResponse])
def get_all_dates(
    pagination: PaginationDep,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Sequence[RowMapping]:
    scheduled: Sequence[RowMapping] = (
        db.execute(
            select(
                ScheduledWorkout.title,
                ScheduledWorkout.duration_minutes,
                ScheduledWorkout.scheduled_at,
                ScheduledWorkout.status,
                WorkoutPlans.title.label("plan"),
            )
            .join(ScheduledWorkout.plan)
            .where(ScheduledWorkout.user_id == current_user.id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        .mappings()
        .all()
    )
    if not scheduled:
        raise HTTPException(
            status_code=404,
            detail="You do not have scheduled workouts",
        )

    return scheduled


@router.get("/{id}", response_model=List[ScheduledWorkoutGetResponse])
def get_date_by_id(
    id: int,
    pagination: PaginationDep,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Sequence[RowMapping]:
    scheduled: Sequence[RowMapping] = (
        db.execute(
            select(
                ScheduledWorkout.title,
                ScheduledWorkout.duration_minutes,
                ScheduledWorkout.scheduled_at,
                ScheduledWorkout.status,
                WorkoutPlans.title.label("plan"),
            )
            .join(ScheduledWorkout.plan)
            .where(
                ScheduledWorkout.user_id == current_user.id,
                ScheduledWorkout.id == id,
            )
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        .mappings()
        .all()
    )
    if not scheduled:
        raise HTTPException(
            status_code=404,
            detail="You do not have scheduled workouts",
        )

    return scheduled


@router.put("/{id}", status_code=205)
def update_schedule(
    schedule: ScheduleUpdate,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    update_schedule: RowMapping = db.execute(
        select(ScheduledWorkout).where(
            ScheduledWorkout.id == id,
        )
    ).scalar_one_or_none()
    if not update_schedule:
        raise HTTPException(
            status_code=404, detail="Nothing scheduld with this id"
        )
    if update_schedule.user_id != current_user.id:
        raise HTTPException(status_code=403)
    new_schedule: dict = schedule.model_dump(exclude_unset=True)
    for k, v in new_schedule.items():
        setattr(update_schedule, k, v)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return Response(status_code=205)


@router.delete("/{id}", status_code=204)
def delete_scheduled(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    schedule_to_delete: RowMapping = db.execute(
        select(ScheduledWorkout).where(
            ScheduledWorkout.id == id,
        )
    ).scalar_one_or_none()
    if not schedule_to_delete:
        raise HTTPException(
            status_code=404, detail="Nothing scheduld with this id"
        )
    if schedule_to_delete.user_id != current_user.id:
        raise HTTPException(status_code=403)

    try:
        db.delete(schedule_to_delete)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response(status_code=204)
