from sqlalchemy.orm import Session
import models
import schemas


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.User):
    db_user = models.User(username=user.username, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    

def create_task(db: Session, task: schemas.Task, user: models.User):
    pass
