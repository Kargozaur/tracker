from fastapi import Depends, HTTPException, APIRouter, Response
from sqlalchemy import select, RowMapping
from sqlalchemy.orm import Session
from typing import List, Optional, Sequence
from schemas.models import WorkoutPlans
from schemas.schemas import (
    PlanUpdate,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
    WorkoutPlanResponseForLoggedUser,
)
from database import get_db
from utility.oauth2 import get_current_user, get_optional_user

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.get(
    "/plans", response_model=List[WorkoutPlanResponseForLoggedUser]
)
def get_workout_plan(
    db=Depends(get_db), current_user=Depends(get_current_user)
):
    workout: Sequence[RowMapping] = (
        db.execute(
            select(
                WorkoutPlans.title.label("title"),
                WorkoutPlans.description.label("description"),
                WorkoutPlans.is_public.label("public"),
                WorkoutPlans.created_at.label("created_at"),
            ).where(
                (WorkoutPlans.user_id == current_user.id)
                | WorkoutPlans.is_public.is_(True)
            )
        )
        .mappings()
        .all()
    )
    if not workout:
        raise HTTPException(
            status_code=404, detail="Workout plans doesn't exists"
        )
    return workout


@router.get("/plans/all", response_model=List[WorkoutPlanResponse])
def get_public_plans(db: Session = Depends(get_db)):
    workout: Sequence[RowMapping] = (
        db.execute(
            select(
                WorkoutPlans.title.label("title"),
                WorkoutPlans.description.label("description"),
                WorkoutPlans.created_at.label("created_at"),
            ).where(WorkoutPlans.is_public.is_(True))
        )
        .mappings()
        .all()
    )

    if not workout:
        raise HTTPException(
            status_code=404, detail="Workout plans doesn't exists"
        )

    return workout


@router.get("/plans/{id}", response_model=WorkoutPlanResponse)
def get_plan_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    query = select(
        WorkoutPlans.title.label("title"),
        WorkoutPlans.description.label("description"),
        WorkoutPlans.created_at.label("created_at"),
    )
    if current_user:
        query = query.where(
            (WorkoutPlans.id == id),
            (WorkoutPlans.user_id == current_user.id)  # type: ignore
            | WorkoutPlans.is_public.is_(True),
        )
        plan: RowMapping | None = db.execute(query).mappings().first()
    else:
        query = query.where(
            WorkoutPlans.id == id, WorkoutPlans.is_public.is_(True)
        )
        plan: RowMapping | None = db.execute(query).mappings().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/plans/create", response_model=WorkoutPlanResponse)
def create_workout_plan(
    plan: WorkoutPlanCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    plan_exists: RowMapping | None = (
        db.execute(
            select(WorkoutPlans).where(
                WorkoutPlans.title == plan.title,
                WorkoutPlans.description == plan.description,
            )
        )
        .mappings()
        .first()
    )
    if plan_exists:
        raise HTTPException(
            status_code=409, detail="Plan already exists"
        )
    new_plan: WorkoutPlans = WorkoutPlans(
        user_id=current_user.id, **plan.model_dump()
    )
    try:
        db.add(new_plan)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=422, detail="wrong credentials"
        )
    finally:
        db.refresh(new_plan)
    return new_plan


@router.delete("/plans/{id}", status_code=204)
def delete_plan(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    delete_plan: RowMapping | None = db.execute(
        select(WorkoutPlans).where(WorkoutPlans.id == id)
    ).scalar_one_or_none()
    if not delete_plan:
        raise HTTPException(
            status_code=404, detail="Plan is not found"
        )
    if delete_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=404, detail="Exercise is not found"
        )
    try:
        db.delete(delete_plan)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.put("/plans/{id}", status_code=205)
def edit_plan(
    id: int,
    plan: PlanUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    update_plan: RowMapping | None = db.execute(
        select(WorkoutPlans).where(WorkoutPlans.id == id)
    ).scalar_one_or_none()

    if not update_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if update_plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")

    new_plan: dict = plan.model_dump(exclude_unset=True)
    try:
        for k, v in new_plan.items():
            setattr(update_plan, k, v)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(update_plan)
    return Response(status_code=205)
