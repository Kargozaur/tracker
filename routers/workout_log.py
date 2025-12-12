from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import List, Optional, Annotated, Sequence
from sqlalchemy import RowMapping, select
from sqlalchemy.orm import Session
from database import get_db
from utility.oauth2 import get_current_user
from schemas.models import ScheduledWorkout, WorkoutLog, WorkoutPlans
from schemas.schemas import (
    PaginationParams,
    UpdateLog,
    WorkoutLogCreate,
    WorkoutLogResponse,
    WorkoutLogCreateResponse,
)

router = APIRouter(prefix="/workout_log", tags=["Scheduled"])
PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


@router.post("/create_log", response_model=WorkoutLogCreateResponse)
def create_log(
    log: WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_cancelled: RowMapping | None = db.execute(
        select(ScheduledWorkout).where(
            ScheduledWorkout.id == log.scheduled_id,
            ScheduledWorkout.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if not check_cancelled:
        raise HTTPException(
            status_code=404, detail="Scheduled workout not found"
        )

    if check_cancelled.status == "cancelled":
        raise HTTPException(
            status_code=409, detail="Workout has been cancelled"
        )

    check_public: RowMapping | None = db.execute(
        select(WorkoutPlans).where(WorkoutPlans.id == log.plan_id)
    ).scalar_one_or_none()
    if not check_public:
        raise HTTPException(
            status_code=404, detail="Plan doesn't exists"
        )
    if check_public.is_public is False:
        raise HTTPException(
            status_code=404, detail="Plan doesn't exists"
        )

    new_log = WorkoutLog(user_id=current_user.id, **log.model_dump())
    try:
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"{Exception}")

    return new_log


@router.get("/", response_model=List[WorkoutLogResponse])
def get_logs(
    pagination: PaginationDep,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    search: Optional[str] = Query("", alias="name"),
):
    logs: Sequence[RowMapping] | None = (
        db.execute(
            select(
                WorkoutPlans.title.label("plan_name"),
                ScheduledWorkout.title.label("scheduled_title"),
                ScheduledWorkout.status,
                ScheduledWorkout.scheduled_at.label("scheduled"),
                WorkoutLog.started_at,
                WorkoutLog.ended_at,
                WorkoutLog.notes,
            )
            .join(WorkoutLog.plan)
            .join(WorkoutLog.scheduled_workout)
            .where(
                WorkoutLog.user_id == current_user.id,
                WorkoutPlans.title.contains(search),
            )
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        .mappings()
        .all()
    )
    if not logs:
        raise HTTPException(
            status_code=404, detail="Logs are not found"
        )
    return logs


@router.get("/{id}", response_model=List[WorkoutLogResponse])
def get_logs_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logs: Sequence[RowMapping] | None = (
        db.execute(
            select(
                WorkoutPlans.title.label("plan_name"),
                ScheduledWorkout.title.label("scheduled_title"),
                ScheduledWorkout.status,
                ScheduledWorkout.scheduled_at.label("scheduled"),
                WorkoutLog.started_at,
                WorkoutLog.ended_at,
                WorkoutLog.notes,
            )
            .join(WorkoutLog.plan)
            .join(WorkoutLog.scheduled_workout)
            .where(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.id == id,
            )
        )
        .mappings()
        .all()
    )
    if not logs:
        raise HTTPException(
            status_code=404, detail="Logs are not found"
        )
    return logs


@router.delete("/{id}", status_code=204)
def delete_log(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    delete_log: RowMapping | None = db.execute(
        select(WorkoutLog).where(WorkoutLog.id == id)
    ).scalar_one_or_none()

    if not delete_log:
        raise HTTPException(
            status_code=404, detail="Log doesn't exists"
        )

    if delete_log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unathorized")

    try:
        db.delete(delete_log)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"{Exception}")
    return Response(status_code=204)


@router.put("/{id}", status_code=205)
def update_log(
    id: int,
    new: UpdateLog,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    update_log: RowMapping | None = db.execute(
        select(WorkoutLog).where(WorkoutLog.id == id)
    ).scalar_one_or_none()

    if not update_log:
        raise HTTPException(
            status_code=404, detail="Log doesn't exist"
        )

    if update_log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    new_log: dict = new.model_dump(exclude_unset=True)
    try:
        for k, v in new_log.items():
            setattr(update_log, k, v)
        db.commit()
        db.refresh(update_log)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"{Exception}")
    return Response(status_code=205)
