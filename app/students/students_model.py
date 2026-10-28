from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.shared.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    pets = relationship("Pet", back_populates="student", cascade="all, delete-orphan")