from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Enum
from database import Base
import enum


class Role(enum.Enum):
    admin = 'admin'
    accountant = 'accountant'
    worker = 'worker'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column('role', Enum(Role, create_constraint=True))
