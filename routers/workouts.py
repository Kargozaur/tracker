from fastapi import Depends, HTTPException, APIRouter, Response
from sqlalchemy import select, RowMapping
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional, Sequence
from schemas.models import WorkoutPlans
from schemas.schemas import (
    PaginationParams,
    PlanUpdate,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
)
from database import get_db
from utility.oauth2 import get_current_user, get_optional_user

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]

router = APIRouter(prefix="/workoutplans", tags=["Workouts"])


@router.get("/", response_model=List[WorkoutPlanResponse])
def get_workout_plan(
    pagination: PaginationDep,
    db=Depends(get_db),
    current_user=Depends(get_optional_user),
) -> Sequence[RowMapping]:
    query = select(
        WorkoutPlans.title.label("title"),
        WorkoutPlans.description.label("description"),
        WorkoutPlans.is_public.label("public"),
        WorkoutPlans.created_at.label("created_at"),
    )
    if not current_user:
        query = query.where(WorkoutPlans.is_public.is_(True))
    elif current_user:
        query = query.where(
            (WorkoutPlans.user_id == current_user.id)
            | WorkoutPlans.is_public.is_(True)
        )
    query = query.limit(pagination.limit).offset(pagination.offset)
    workout: Sequence[RowMapping] = db.execute(query).mappings().all()
    if not workout:
        raise HTTPException(
            status_code=404, detail="Workout plans doesn't exists"
        )
    return workout


@router.get("/{id}", response_model=WorkoutPlanResponse)
def get_plan_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user),
) -> RowMapping:
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
) -> WorkoutPlans:
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
) -> None:
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
) -> Response:
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
