import enum
from database import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


class Role(enum.Enum):
    admin = 'admin'
    accountant = 'accountant'
    worker = 'worker'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    role = Column('role', Enum(Role, create_constraint=True))
    tasks: Mapped[List['Task']] = relationship()
    

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    user_id = Mapped[int] = mapped_column(ForeignKey('users.id'))
    user = Mapped['User'] = relationship(back_populates='tasks')
