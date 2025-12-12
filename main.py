from fastapi import FastAPI
import schemas.models as models
import database
from routers import (
    exercises,
    scheduled,
    users,
    workout_items,
    workout_log,
    workouts,
)

models.Base.metadata.create_all(database.engine)

app = FastAPI()


@app.get("/")
def main():
    return {"data": "hello"}


app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(workout_items.router)
app.include_router(scheduled.router)
app.include_router(workout_log.router)
