# This is a back end service for the Workout tracking app

# Gym/Workout Tracking App - Backend Service

A FastAPI-based backend service for a gym and workout tracking application. Features include JWT authentication, data ownership verification, and robust data validation using Pydantic.

## Stack

- **Framework**: FastAPI
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker & Docker Compose installed
- Git

## Installation & Setup

### 1. Clone the Repository
```
git clone https://github.com/Kargozaur/tracker
cd tracker
```
### 2. Generate secret_key. Secret key should not change after you wrote the initial user.

```
openssl rand -hex <desired length of the key>
```

### 3. Add this key to the .env file. Your .env file should look something like this:

```
SECRET_KEY=<your key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql+psycopg2://<database_user>:<database_password>@<host>:<database port>/<database_name>
```

### 4. After that you need configure .env.db file for the database. It has to look something like this:

```
env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
POSTGRES_DB=tracer
```

### 5. To run the application, you need to run:

```
docker-compose up --build -d
```

#### To ensure that container is running you can write:
```
docker ps
```

#### To stop the application simply write 
```
docker-compose down
```

#### Also you need to run a seed/exercise_seed.py to have an initial data for the exercise_category table


### 6. To test the API you may user Swagger(host/docs) or postman

## API endpoints overview

### 1. User

#### POST /signin - User registration
#### POST/login - Login user. Endpoint returns JWT tocken

### 2. Exercise

#### GET /exercise - Get exercises. Returns all exercises that either public, or public and owned by the user

#### GET /exercise/{id} - Get a single exercise. If exercise is not public or not owned by the user returns an error.

#### POST /create_exercise - Create a single exercise. Endpoint ensures that category has to exist and user need to be logged in

#### PUT /exercise/{id} - Change data for the exercise. You can change either title, description or set in hidden/global

#### DELETE /exercise/{id} - Delete exercise

### 3. Workouts

#### GET /workoutplans/ - Return all available plans for the user. If user is none, than returns all public plans. Endpoint supports pagination by the limit and offset
#### GET /workoutplans/{id} - Returns plan by id. If plan is not global and wrong credentials provided, returns 404.

#### POST /workoutplans/plans/create - Create a plan. 

#### PUT /workoutplans/{id} - Edit the plan. It can be changed either by title, description or availability to the others(is_global)

#### DELETE /workoutplans/plans/{id} - Delete the plan. Raises error if user is not the owner of the plan.

#### GET /workout_items/ - Returns all items for the user

#### GET /workout_items/{id} - Returns single item for the user

#### POST /workot_items/create - Creates an item for the user. Can contain a list in the body for the exercises

#### PUT /workout_items/{pid}/{id} - Edit an item in the plan.

#### DELETE /workout_items/{pid}/{id} - Deletes an single item for the plan

#### DELETE /workout_items/{pid} - Deletes all entrys for the plan.

### 4. Scheduled

#### GET /scheduled/ - Returns all scheduled workouts, their statuses etc.

#### GET /scheduled/{id} - Get schedule by id

#### POST /scheduled/create - Schedule a workout

#### PUT/scheduled/{id} - Edit the schedule. User can change either title, schedule date(scheduled_at), duration, status. 

#### DELETE /scheduled/{id} - Delete schedule

#### GET /workout_log/ - Returns all actual logs for the user. 

#### GET /workout_log/{id} - Returns a single log for the user.

#### POST /workout_log/create_log - Create log for the user

#### PUT /workout_log/{id} - User can edit date started(started_at), when ended (ended_at) and their notes.

#### DELETE /workout_log/{id} - Delete log

### 5. Workout log items

#### POST /workout_log_items/create_log_item - Creates log entry for the user

#### GET /workout_log_items/{log_id}/all - Returns all items for the log_id

#### PUT /workout_log_items/{log_id} - edit entrys with the same log_id. 

#### DELETE /workout_log_items/{log_id} - delete log