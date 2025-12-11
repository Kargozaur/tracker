from typing import Any, List, Optional, Annotated
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    AfterValidator,
)
from pydantic import model_validator
from pydantic_settings import SettingsConfigDict
from datetime import datetime, timezone
from enum import Enum


def is_positive(value: float | int) -> float | int:
    if value <= 0:
        raise ValueError("Value has to be positive")
    return value


def validate_future_datetime(date: datetime) -> datetime:
    now = datetime.now(timezone.utc)

    if date.tzinfo is None:
        raise ValueError("Date has to contain timezone")

    date_utc = date.astimezone(timezone.utc)
    if date_utc <= now:
        raise ValueError("Date has to be in the future")

    return date


FutureDate = Annotated[
    datetime, AfterValidator(validate_future_datetime)
]


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
    plan_id: int
    title: str = Field(..., min_length=8)
    duration_minutes: Annotated[int, AfterValidator(is_positive)]
    scheduled_at: FutureDate
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
    plan_id: int
    exercise_id: list[int]
    sets: Annotated[int, AfterValidator(is_positive)]
    reps: str
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


class WorkoutItemsResponse(BaseModel):
    id: int
    plan_id: int
    exercise_name: str
    exercise_description: str
    exercise_purpose: str
    sets: int
    reps: str

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutItemsCreateResponse(BaseModel):
    id: int
    plan_id: int
    exercise_id: int

    @model_validator(mode="before")
    @classmethod
    def convert_exercise_to_list(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(
            data.get("exercise_id"), int
        ):
            data["exercise_id"] = [data["exercise_id"]]
        return data

    model_config = SettingsConfigDict(from_attributes=True)


class WorkoutItemsUpdate(BaseModel):
    sets: Optional[str] = None
    reps: Optional[str] = None
    weight: Optional[float] = None
    rest_seconds: Optional[int] = None


class ScheduledWorkoutResponse(BaseModel):
    id: int
    title: str
    scheduled_at: datetime
    duration_minutes: int
    status: WorkoutStatus
    plan: WorkoutPlanResponse

    model_config = SettingsConfigDict(from_attributes=True)


class ScheduledWorkoutGetResponse(BaseModel):
    title: str
    duration_minutes: int
    scheduled_at: datetime
    status: WorkoutStatus
    plan: str


class ScheduleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=6)
    scheduled_at: Annotated[
        Optional[datetime], AfterValidator(validate_future_datetime)
    ] = None
    duration_minutes: Annotated[
        Optional[int], AfterValidator(is_positive)
    ] = None
    status: Optional[WorkoutStatus] = None


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
    sets: Annotated[int, AfterValidator(is_positive)]
    reps: str
    weight: Annotated[float, AfterValidator(is_positive)]
    rest_seconds: Annotated[int, AfterValidator(is_positive)]


class LoginRequest(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class PaginationParams(BaseModel):
    limit: int = Field(5, ge=5, le=20)
    offset: int = Field(0, ge=0, le=20)
