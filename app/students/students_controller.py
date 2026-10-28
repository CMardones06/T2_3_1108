
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)
from app.students.students_service import StudentsService

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("")
def find_all(db: Annotated[Session, Depends(get_db)]) -> StudentList:
    service = StudentsService(db)
    return service.find_all()


@router.get("/{studentId}")
def find_by_id(
    student_id: Annotated[str, Path(alias="studentId")],
    db: Annotated[Session, Depends(get_db)],
) -> Student:
    service = StudentsService(db)
    return service.find_by_id(student_id)


@router.post("", status_code=201)
def create(
    body: CreateStudentDto,
    db: Annotated[Session, Depends(get_db)],
) -> Student:
    service = StudentsService(db)
    return service.create(body)


@router.patch("/{studentId}")
def update(
    student_id: Annotated[str, Path(alias="studentId")],
    body: UpdateStudentDto,
    db: Annotated[Session, Depends(get_db)],
) -> Student:
    service = StudentsService(db)
    return service.update(student_id, body)


@router.delete("/{studentId}")
def delete(
    student_id: Annotated[str, Path(alias="studentId")],
    db: Annotated[Session, Depends(get_db)],
) -> Student:
    service = StudentsService(db)
    return service.delete(student_id)
