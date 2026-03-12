from sqlalchemy.orm import Session
from app.models import Student


def ensure_default_student(db: Session):
    row = db.query(Student).filter(Student.id == 1).first()
    if not row:
        row = Student(id=1, name="默认学生")
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def list_students(db: Session):
    ensure_default_student(db)
    return db.query(Student).order_by(Student.id.asc()).all()


def create_student(db: Session, name: str):
    row = Student(name=name)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row