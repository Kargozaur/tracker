from fastapi import FastAPI
import schemas.models as models
import database

models.Base.metadata.create_all(database.engine)

app = FastAPI()


@app.get("/")
def main():
    return {"data": "hello"}
