from database import Base
from sqlalchemy import (
    String,
    Boolean,
    text,
    Integer,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.types import TIMESTAMP


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    workout_plans = relationship(
        "WorkoutPlans", back_populates="user"
    )
    scheduled_workouts = relationship(
        "ScheduledWorkout", back_populates="user"
    )
    workout_logs = relationship("WorkoutLog", back_populates="user")


class ExerciseCategory(Base):
    __tablename__ = "exercise_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )

    exercises = relationship("Exercise", back_populates="category")


class Exercise(Base):
    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("exercise_category.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    category = relationship(
        "ExerciseCategory", back_populates="exercises"
    )
    workout_items = relationship(
        "WorkoutItems", back_populates="exercise"
    )
    log_items = relationship(
        "WorkoutLogItems", back_populates="exercise"
    )


class WorkoutPlans(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(
        String(500), nullable=True
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    user = relationship("User", back_populates="workout_plans")
    items = relationship("WorkoutItems", back_populates="plan")
    scheduled = relationship(
        "ScheduledWorkout", back_populates="plan"
    )
    logs = relationship("WorkoutLog", back_populates="plan")


class WorkoutItems(Base):
    __tablename__ = "workout_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercise.id"), nullable=False
    )

    sets: Mapped[int] = mapped_column(
        Integer, server_default=text("4")
    )
    reps: Mapped[str] = mapped_column(
        String(20), server_default=text("'10'")
    )
    weight: Mapped[float] = mapped_column(DECIMAL(5, 2))
    rest_seconds: Mapped[int] = mapped_column(Integer)

    plan = relationship("WorkoutPlans", back_populates="items")
    exercise = relationship(
        "Exercise", back_populates="workout_items"
    )


class ScheduledWorkout(Base):
    __tablename__ = "scheduled_workout"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plans.id", ondelete="SET NULL")
    )

    title: Mapped[str] = mapped_column(String(100))
    scheduled_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    duration_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20), server_default=text("'pending'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    user = relationship("User", back_populates="scheduled_workouts")
    plan = relationship("WorkoutPlans", back_populates="scheduled")
    logs = relationship(
        "WorkoutLog", back_populates="scheduled_workout"
    )


class WorkoutLog(Base):
    __tablename__ = "workout_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_id: Mapped[int] = mapped_column(
        ForeignKey("scheduled_workout.id", ondelete="SET NULL")
    )
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plans.id", ondelete="SET NULL")
    )

    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    ended_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    notes: Mapped[str] = mapped_column(String(300))

    user = relationship("User", back_populates="workout_logs")
    scheduled_workout = relationship(
        "ScheduledWorkout", back_populates="logs"
    )
    plan = relationship("WorkoutPlans", back_populates="logs")
    items = relationship("WorkoutLogItems", back_populates="log")


class WorkoutLogItems(Base):
    __tablename__ = "workout_log_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    log_id: Mapped[int] = mapped_column(
        ForeignKey("workout_log.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercise.id")
    )
    set_number: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(DECIMAL(5, 2))
    notes: Mapped[str] = mapped_column(String(300))

    log = relationship("WorkoutLog", back_populates="items")
    exercise = relationship("Exercise", back_populates="log_items")
