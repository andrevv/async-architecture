from typing import List
from pydantic import BaseModel
import models


class User(BaseModel):
    username: str
    role: models.Role


class Task(BaseModel):
    title: str


class UserWithTasks(BaseModel):
    username: str
    tasks: List[Task]
