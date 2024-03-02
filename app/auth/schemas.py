from pydantic import BaseModel
import models


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    role: models.Role


class UserCreate(BaseModel):
    username: str
    password: str
    role: models.Role
