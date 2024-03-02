from aiokafka import AIOKafkaConsumer
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database import SessionLocal, engine
import crud
import models
import asyncio
import schemas


SECRET_KEY = "e6sxwwm0ewbp7ngguovbvbkc3d8bvtqd08"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='http://localhost:8000/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def listen():
    consumer = AIOKafkaConsumer('users', bootstrap_servers='localhost:9092')
    await consumer.start()
    try:
        async for msg in consumer:
            db = SessionLocal()
            s = msg.value.decode('utf-8')
            user = schemas.User.model_validate_json(s)
            crud.create_user(db, user=user)
            db.close()
    finally:
        await consumer.stop()


asyncio.create_task(listen())


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credential_exception
        user = crud.get_user_by_username(db, username=username)
        if user is None:
            raise credential_exception
        return user
    except JWTError:
        raise credential_exception


@app.get('/tasks/')
async def read_tasks(current_user: models.User = Depends(get_current_user)):
    return current_user.username


@app.post('/tasks/')
async def create_task(task: schemas.Task, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    crud.create_task(db, task=task, user=current_user)
