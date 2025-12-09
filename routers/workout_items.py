from fastapi import HTTPException, APIRouter, Depends, Response
from sqlalchemy import select, RowMapping
from sqlalchemy.orm import Session
from typing import List, Sequence
from database import get_db
from schemas.models import Exercise, WorkoutItems, WorkoutPlans
from schemas.schemas import (
    WorkoutItemCreate,
    WorkoutItemsCreateResponse,
    WorkoutItemsResponse,
    WorkoutItemsUpdate,
)
from utility.oauth2 import get_current_user

router = APIRouter(prefix="/workout_items", tags=["Workouts"])


@router.get("/", response_model=List[WorkoutItemsResponse])
def get_items(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Sequence[RowMapping]:
    items: Sequence[RowMapping] = (
        db.execute(
            select(
                WorkoutItems.id,
                WorkoutItems.plan_id,
                Exercise.name.label("exercise_name"),
                Exercise.description.label("exercise_description"),
                WorkoutPlans.title.label("exercise_purpose"),
                WorkoutItems.sets,
                WorkoutItems.reps,
            )
            .join(WorkoutItems.exercise)
            .join(WorkoutItems.plan)
            .where(WorkoutPlans.user_id == current_user.id)
        )
        .mappings()
        .all()
    )
    if not items:
        raise HTTPException(
            status_code=404, detail="Items are not found"
        )

    return items


@router.get("/{id}", response_model=List[WorkoutItemsResponse])
def get_item_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Sequence[RowMapping]:
    items: Sequence[RowMapping] = (
        db.execute(
            select(
                WorkoutItems.id,
                WorkoutItems.plan_id,
                Exercise.name.label("exercise_name"),
                Exercise.description.label("exercise_description"),
                WorkoutPlans.title.label("exercise_purpose"),
                WorkoutItems.sets,
                WorkoutItems.reps,
            )
            .join(WorkoutItems.exercise)
            .join(WorkoutItems.plan)
            .where(
                WorkoutPlans.user_id == current_user.id,
                WorkoutItems.plan_id == id,
            )
        )
        .mappings()
        .all()
    )
    if not items:
        raise HTTPException(
            status_code=404, detail="Items are not found"
        )

    return items


@router.post(
    "/create", response_model=List[WorkoutItemsCreateResponse]
)
def create_workout_item(
    item: WorkoutItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list:
    get_plan: RowMapping | None = (
        db.execute(
            select(WorkoutPlans.id).where(
                WorkoutPlans.id == item.plan_id,
                (
                    (WorkoutPlans.user_id == current_user.id)
                    | WorkoutPlans.is_public.is_(True)
                ),
            )
        )
        .mappings()
        .first()
    )
    if not get_plan:
        raise HTTPException(
            status_code=404, detail="Plan doesn't exists"
        )

    get_exercises: Sequence[RowMapping] | None = (
        db.execute(
            select(Exercise.id).where(
                Exercise.id.in_(item.exercise_id)
            )
        )
        .mappings()
        .all()
    )
    if not get_exercises:
        raise HTTPException(
            status_code=404, detail="Exercises are not found"
        )
    new_items = []
    try:
        for exercise_id in item.exercise_id:
            new_item = WorkoutItems(
                plan_id=item.plan_id,
                exercise_id=exercise_id,
                sets=item.sets,
                reps=item.reps,
                weight=item.weight,
                rest_seconds=item.rest_seconds,
            )
            db.add(new_item)
            new_items.append(new_item)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return new_items


@router.put("/{pid}/{id}", status_code=205)
def edit_plan(
    pid: int,
    id: int,
    plan_data: WorkoutItemsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    get_plan: WorkoutPlans | None = db.execute(
        select(WorkoutPlans).where(WorkoutPlans.id == pid)
    ).scalar_one_or_none()
    if not get_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if (
        get_plan.user_id != current_user.id
        and get_plan.is_public is True
    ):
        raise HTTPException(
            status_code=403, detail="You cannot change this plan"
        )

    plan_obj: WorkoutItems | None = db.execute(
        select(WorkoutItems).where(
            WorkoutItems.id == id,
            WorkoutItems.plan_id == pid,
        )
    ).scalar_one_or_none()

    if not plan_obj:
        raise HTTPException(status_code=404, detail="Plan Not found")

    item: WorkoutItems | None = db.execute(
        select(WorkoutItems).where(WorkoutItems.id == id)
    ).scalar_one_or_none()
    update_plan = plan_data.model_dump(exclude_unset=True)

    try:
        for k, v in update_plan.items():
            setattr(item, k, v)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.refresh(item)

    return Response(status_code=205)


@router.delete("/{pid}/{id}", status_code=205)
def delete_exercise(
    pid: int,
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    get_plan: WorkoutPlans | None = db.execute(
        select(WorkoutPlans).where(WorkoutPlans.id == pid)
    ).scalar_one_or_none()
    if not get_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if (
        get_plan.user_id != current_user.id
        and get_plan.is_public is True
    ):
        raise HTTPException(
            status_code=403, detail="You cannot change this plan"
        )

    plan_obj: WorkoutItems | None = db.execute(
        select(WorkoutItems).where(
            WorkoutItems.id == id,
            WorkoutItems.plan_id == pid,
        )
    ).scalar_one_or_none()

    if not plan_obj:
        raise HTTPException(status_code=404, detail="Plan Not found")

    item: WorkoutItems | None = db.execute(
        select(WorkoutItems).where(WorkoutItems.id == id)
    ).scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=404, detail="Plan doesn't exist"
        )

    try:
        db.delete(item)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response(status_code=204)


@router.delete("/{pid}", status_code=204)
def delete_plan(
    pid: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_plan = db.execute(
        select(WorkoutPlans).where(WorkoutPlans.id == pid)
    ).scalar_one_or_none()

    if not get_plan:
        raise HTTPException(
            status_code=404, detail="Plan doesn't exist"
        )

    if get_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can not change this plan"
        )
    try:
        db.query(WorkoutItems).filter(
            WorkoutItems.plan_id == pid
        ).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response(status_code=204)
