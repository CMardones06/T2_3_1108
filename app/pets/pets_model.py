from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.database import Base

class Pet(Base):
    __tablename__ = "pets"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    name = Column(String(50), nullable=False)
    species = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    student = relationship("Student", back_populates="pets")