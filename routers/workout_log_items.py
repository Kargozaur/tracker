from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Sequence
from sqlalchemy import RowMapping, select
from sqlalchemy.orm import Session
from database import get_db
from schemas.schemas import (
    WorkoutLogItemsRequest,
    WorkoutLogItemsUpdate,
)
from utility.oauth2 import get_current_user
from schemas.models import WorkoutLog, WorkoutLogItems

router = APIRouter(
    prefix="/workout_log_items", tags=["Workout log Items"]
)


@router.post("/create_log_item")
def create_log_items(
    data: WorkoutLogItemsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    workout_log: RowMapping | None = db.execute(
        select(WorkoutLog).where(
            WorkoutLog.id == data.log_id,
            WorkoutLog.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if not workout_log:
        raise HTTPException(status_code=404, detail="Log not found")

    created_items: list = []

    try:
        for item in data.items:
            log_item = WorkoutLogItems(
                log_id=data.log_id,
                exercise_id=item.exercise_id,
                workout_item_id=item.workout_item_id,
                set_number=item.set_number,
                reps=item.reps,
                weight=item.weight,
                notes=item.notes,
            )
            db.add(log_item)
            created_items.append(log_item)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=422)
    return {
        "log_id": data.log_id,
        "items_created": len(created_items),
    }


@router.get("/{log_id}/all")
def get_log_items(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    log: Sequence[WorkoutLogItems] = (
        db.execute(
            select(WorkoutLogItems)
            .join(WorkoutLogItems.log)
            .where(
                WorkoutLogItems.log_id == log_id,
                WorkoutLog.user_id == current_user.id,
            )
        )
        .scalars()
        .all()
    )

    if not log:
        raise HTTPException(
            status_code=404, detail="Log doesn't exist"
        )

    return log


@router.put("/{log_id}", status_code=205)
def update_log_items(
    data: WorkoutLogItemsUpdate,
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    log: Sequence[WorkoutLogItems] = db.execute(
        select(WorkoutLogItems)
        .join(WorkoutLogItems.log)
        .where(
            WorkoutLogItems.log_id == log_id,
            WorkoutLog.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if not log:
        raise HTTPException(
            status_code=404, detail="Log doesn't exist"
        )

    update_log: dict = data.model_dump(exclude_unset=True)

    try:
        for k, v in update_log.items():
            setattr(log, k, v)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"{Exception}")
    return Response(status_code=205)


@router.delete("/{log_id}", status_code=204)
def delete_log_items(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    log: Sequence[WorkoutLogItems] = db.execute(
        select(WorkoutLogItems)
        .join(WorkoutLogItems.log)
        .where(
            WorkoutLogItems.log_id == log_id,
            WorkoutLog.user_id == current_user.id,
        )
    ).scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    try:
        db.query(WorkoutLogItems).filter(
            WorkoutLogItems.log_id == log_id
        ).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"{Exception}")
    return Response(status_code=204)
