from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class QuestionHistory(Base):
    __tablename__ = "question_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    steps = Column(Text, nullable=False)  # JSON 字符串
    knowledge_points = Column(Text, nullable=False)  # JSON 字符串
    similar_question = Column(Text, nullable=False)
    is_wrong = Column(Boolean, default=False, nullable=False)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False,
                        default=1)

class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)