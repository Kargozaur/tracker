from typing import List, Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, AfterValidator
from pydantic import model_validator
from pydantic_settings import SettingsConfigDict
from datetime import datetime
from enum import Enum


def is_positive(value: float | int) -> float | int:
    if value < 0:
        raise ValueError("Value has to be positive")
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
    back = "back"
    shoulders = "shoulders"
    legs = "legs"
    chest = "chest"
    biceps = "biceps"
    abs = "abs"


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
    name: str = Field(..., min_length=8, max_length=100)
    category_id: int
    description: Optional[str] = ""
    is_global: Optional[bool] = False


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
                (self.ended_at - self.started_at).total_seconds()
                // 60
            )
        return self


class WorkoutItemCreate(BaseModel):
    exercise_id: Annotated[int, AfterValidator(is_positive)]
    sets: Annotated[int, AfterValidator(is_positive)]
    reps: Annotated[int, AfterValidator(is_positive)]
    weight: Annotated[float, AfterValidator(is_positive)]
    rest_seconds: Annotated[int, AfterValidator(is_positive)]


class WorkoutPlanCreate(BaseModel):
    title: str = Field(..., min_length=6)
    description: Optional[str] = ""
    is_public: Optional[bool] = False


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = SettingsConfigDict(from_attributes=True)


class ExerciseResponse(BaseModel):
    category: str
    title: str
    description: Optional[str]

    model_config = SettingsConfigDict(from_attributes=True)


class ExerciseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=6)
    description: Optional[str] = None
    is_global: bool

    model_config = SettingsConfigDict(from_attributes=True)


class PlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=6)
    description: Optional[str] = None
    is_public: bool


class ExerciseCreateResponse(BaseModel):
    id: int
    created_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutLogItemsResponse(BaseModel):
    id: int
    set_numbers: int
    reps: int
    weight: float
    notes: Optional[str]
    exercise: ExerciseResponse

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutItemResponse(BaseModel):
    id: int
    sets: int
    reps: int
    weight: float
    rest_seconds: int
    exercise: ExerciseResponse

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutPlanResponse(BaseModel):
    title: str
    description: str
    created_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutPlanResponseForLoggedUser(WorkoutPlanResponse):
    public: bool


class ScheduledWorkoutResponse(BaseModel):
    id: int
    title: str
    scheduled_at: datetime
    duration_minutes: int
    status: WorkoutStatus
    created_at: datetime

    user: UserResponse
    plan: WorkoutPlanResponse

    model_config = SettingsConfigDict(from_attributes=True)


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

    model_config = SettingsConfigDict(from_attributes=True)


class ExerciseS(BaseModel):
    name: str
    description: str
    category_id: int

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutItemsS(BaseModel):
    plan_id: int
    exercise_id: int
    sets: Annotated[int, is_positive]
    reps: str
    weight: Annotated[float, is_positive]
    rest_seconds: Annotated[int, is_positive]


class LoginRequest(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
