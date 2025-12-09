from fastapi import FastAPI
import schemas.models as models
import database
from routers import exercises, users, workout_items, workouts

models.Base.metadata.create_all(database.engine)

app = FastAPI()


@app.get("/")
def main():
    return {"data": "hello"}


app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(workout_items.router)
