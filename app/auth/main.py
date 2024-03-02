from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas
import models
import crud
import crypto
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from kafka import KafkaProducer


SECRET_KEY = "e6sxwwm0ewbp7ngguovbvbkc3d8bvtqd08"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
KAFKA_BOOTSTRAP_SERVERS='localhost:9092'
KAFKA_TOPIC='users'
KAFKA_CONSUMER_GROUP='users'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


producer = KafkaProducer(bootstrap_servers='localhost:9092')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


origins = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8002',
    'http://127.0.0.1:8002',
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


def get_user(db, username: str):
    if username in db:
        user = db[username]
        return models.User(**user)


def authenticate(db, username: str, password: str):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return False
    if not crypto.verify_password(password, user.password):
        return False
    
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
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


@app.post('/token/', response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect user name or password', headers={'WWW-Authenticate': 'Bearer'})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/users/', response_model=list[schemas.User])
async def read_users(current_user = Depends(get_current_user), db = Depends(get_db)):
    if current_user.username != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    return crud.get_users(db)


@app.post('/users/', response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != models.Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already registered.')
    
    schema_user = schemas.User(username=user.username, role=user.role)
    message = bytes(schema_user.model_dump_json(), 'utf-8')
    producer.send('users', message)
    
    return crud.create_user(db, user=user)


@app.post('/users/change_role', response_model=schemas.User)
async def update_user_role(user: schemas.User, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    db_user = crud.change_user_role(db, user.username, user.role)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
    
    return db_user


@app.get('/users/me/', response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return schemas.User(username=current_user.username, role=current_user.role)
