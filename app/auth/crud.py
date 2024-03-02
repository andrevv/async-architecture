from sqlalchemy.orm import Session
import models
import schemas
import crypto


def get_users(db: Session):
    return db.query(models.User).all()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = crypto.hash_password(user.password)
    db_user = models.User(username=user.username, password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def change_user_role(db: Session, username: str, role: models.Role):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        return None
    
    db_user.role = role
    db.commit()
    db.refresh(db_user)

    return db_user
