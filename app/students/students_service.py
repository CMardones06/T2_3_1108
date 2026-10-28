from uuid import uuid4

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.students.students_model import Student as StudentModel
from app.pets.pets_model import Pet as PetModel
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.shared.types import FieldErrors
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)

STUDENT_NOT_FOUND = "Estudiante no encontrado"

class StudentsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = StudentsRepository(db)

    def find_all(self) -> StudentList:
        students = self.repository.find_all()

        students = sorted(
            students,
            key=lambda student: student.created_at,
            reverse=True,
        )

        return StudentList(
            total=len(students),
            items=[Student.model_validate(student) for student in students],
    )

    def find_by_id(self, student_id: str) -> Student:
        student = self.repository.find_by_id(student_id)

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STUDENT_NOT_FOUND,
            )

        return Student.model_validate(student)


    def create(self, data: CreateStudentDto) -> Student:
        self.assert_no_conflicts(data)

        now = utc_now()
        student_id = str(uuid4())

        student = StudentModel(
            id=student_id,
            name=data.name,
            username=data.username,
            email=str(data.email),
            age=data.age,
            created_at=now,
            updated_at=now,
        )

        try:
            saved_student = self.repository.save(student)

            pet_names = set()

            for pet_data in data.pets:
  
                if pet_data.name in pet_names:
                    raise conflict({
                        "pets": {
                            "message": "No puede haber mascotas con el mismo nombre"
                        }
                    })

                pet_names.add(pet_data.name)

                pet = PetModel(
                    id=str(uuid4()),
                    student_id=student_id,
                    name=pet_data.name,
                    species=pet_data.species,
                    age=pet_data.age,
                    created_at=now,
                    updated_at=now,
                )

                self.db.add(pet)

            self.db.flush()


            self.db.commit()

            self.db.refresh(saved_student)

            return Student.model_validate(saved_student)

        except Exception:
            # Si falla cualquier operación, deshacer toda la transacción.
            self.db.rollback()
            raise


    
    def update(self, student_id: str, data: UpdateStudentDto) -> Student:
        student = self.repository.find_by_id(student_id)

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STUDENT_NOT_FOUND,
            )

        self.assert_no_conflicts(data, except_id=student_id)

        changes = data.model_dump(exclude_unset=True, exclude_none=True)

        for field, value in changes.items():
            setattr(student, field, value)

        student.updated_at = utc_now()

        try:
            saved_student = self.repository.save(student)
            self.db.commit()
            self.db.refresh(saved_student)

            return Student.model_validate(saved_student)

        except Exception:
            self.db.rollback()
            raise


    
    def delete(self, student_id: str) -> Student:
        student = self.repository.find_by_id(student_id)

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STUDENT_NOT_FOUND,
            )

        deleted_student = Student.model_validate(student)

        try:
            self.repository.delete(student_id)
            self.db.commit()

            return deleted_student

        except Exception:
            self.db.rollback()
            raise


    def assert_no_conflicts(
        self,
        data: CreateStudentDto | UpdateStudentDto,
        except_id: str | None = None,
    ) -> None:
        errors: FieldErrors = {}

        if data.email:
            existing = self.repository.find_by_email(data.email)
            if existing and existing.id != except_id:
                errors["email"] = {"message": "El correo electrónico ya está en uso"}

        if data.username:
            existing = self.repository.find_by_username(data.username)
            if existing and existing.id != except_id:
                errors["username"] = {"message": "El nombre de usuario ya está en uso"}

        if errors:
            raise conflict(errors)
