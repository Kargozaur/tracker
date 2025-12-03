from typing import List, Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, AfterValidator, model_validator
from datetime import datetime
from enum import Enum


def is_positive(value: float | int) -> float:
    if value < 0:
        raise ValueError(f"Value has to be positive")
    return value


class BaseEnum(str, Enum):
    pass


class WorkoutStatus(BaseEnum):
    pending = "pending"
    stopped = "stopped"
    done = "done"
    missed = "missed"
    cancelled = "cancelled"


class ExerciseType(BaseEnum):
    cardio = "cardio"
    strength = "strength"
    flexibility = "flexibility"
    legs = "legs"
    chest = "chest"
    hands = "hands"


class WorkoutLogItemCreate(BaseModel):
    exercise_id: Annotated[int, AfterValidator(is_positive)]
    set_number: Annotated[int, AfterValidator(is_positive)]
    reps: Annotated[int, AfterValidator(is_positive)]
    weight: Annotated[float, AfterValidator(is_positive)]
    notes: Optional[str]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=40)


class UserLogin(UserCreate):
    pass


class ScheduledWorkoutCreate(BaseModel):
    title: str = Field(..., min_length=8)
    plan: Annotated[List[str], Field(min_length=1)]
    duration: Annotated[int, AfterValidator(is_positive)]
    status: WorkoutStatus = WorkoutStatus.pending


class ExercisesCreate(BaseModel):
    title: str = Field(..., min_length=8, max_length=100)
    category: ExerciseType
    description: Optional[str] = ""


class WorkoutLogCreate(BaseModel):
    plan_id: int
    notes: Optional[str] = ""
    items: List[WorkoutLogItemCreate]
    started_at: datetime
    ended_at: datetime
    duration_minutes: Optional[int] = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.started_at > self.ended_at:
            raise ValueError("ended_at must be higher than")

        if self.duration_minutes is None:
            self.duration_minutes = int(
                (self.ended_at - self.started_at).total_seconds // 60
            )
        return self


class WorkoutItemCreate(BaseModel):
    exercise_id: Annotated[int, AfterValidator(is_positive)]
    sets: Annotated[int, AfterValidator(is_positive)]
    reps: Annotated[int, AfterValidator(is_positive)]
    weight: Annotated[float, AfterValidator(is_positive)]
    rest_seconds: Annotated[int, AfterValidator(is_positive)]


class WorkoutPlanCreate(BaseModel):
    title: str = Field(..., min_length=8)
    description: Optional[str] = ""
    exercises: Annotated[List[WorkoutItemCreate], Field(min_length=1)]
    is_public: bool = False


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseCategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attribute = True


class ExerciseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: ExerciseCategoryResponse
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutLogItemsResponse(BaseModel):
    id: int
    set_numbers: int
    reps: int
    weight: float
    notes: Optional[str]
    exercise: ExerciseResponse

    class Config:
        from_attributes = True


class ScheduledWorkoutResponse(BaseModel):
    id: int
    title: str
    scheduled_at: datetime
    duration_minutes: int
    status: WorkoutStatus
    created_at: datetime

    user: UserResponse
    plan: WorkoutPlanResponse | None

    class Config:
        from_attributes = True


class WorkoutItemResponse(BaseModel):
    id: int
    sets: int
    reps: int
    weight: float
    rest_seconds: int
    exercise: ExerciseResponse

    class Config:
        from_attributes = True


class WorkoutPlanResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_public: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutPlanGeneralResponse(WorkoutPlanResponse):
    user_id: int
    exercises: List[WorkoutItemResponse]


class WorkoutLogResponse(BaseModel):
    id: int
    notes: Optional[str]
    started_at: datetime
    ended_at: datetime
    duration_minutes: float
    plan: WorkoutPlanResponse
    items: List[WorkoutLogItemsResponse]

    class Config:
        from_attribute = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
