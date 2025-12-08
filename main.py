from fastapi import FastAPI
import schemas.models as models
import database
from routers import exercises, users, workouts

models.Base.metadata.create_all(database.engine)

app = FastAPI()


@app.get("/")
def main():
    return {"data": "hello"}


app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
