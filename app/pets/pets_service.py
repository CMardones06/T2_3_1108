from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.pets.pets_model import Pet as PetModel
from app.pets.pets_repository import PetsRepository, pets_repository
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.students.students_service import StudentsService


class PetsService:
    def __init__(self, repository: PetsRepository) -> None:
        self.repository = repository

    def find_all_for_student(self, db: Session, student_id: str) -> PetList:
        StudentsService(db).find_by_id(student_id)

        pets = self.repository.find_all_by_student(db, student_id)
        pets_sorted = sorted(
            pets,
            key=lambda pet: pet.created_at,
            reverse=True,
        )

        return PetList(
            total=len(pets_sorted),
            items=[Pet.model_validate(p) for p in pets_sorted],
        )

    def create(self, db: Session, student_id: str, data: CreatePetDto) -> Pet:
        StudentsService(db).find_by_id(student_id)
        self.assert_no_conflicts(db, student_id, data)

        now = utc_now()
        pet = PetModel(
            id=str(uuid4()),
            student_id=student_id,
            name=data.name,
            species=data.species,
            age=data.age,
            created_at=now,
            updated_at=now,
        )

        saved_pet = self.repository.save(db, pet)
        return Pet.model_validate(saved_pet)

    def update(
        self, db: Session, student_id: str, pet_id: str, data: UpdatePetDto
    ) -> Pet:
        existing = self.find_owned_model(db, student_id, pet_id)
        self.assert_no_conflicts(db, student_id, data, except_id=pet_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing, key, value)

        existing.updated_at = utc_now()

        saved_pet = self.repository.save(db, existing)
        return Pet.model_validate(saved_pet)

    def delete(self, db: Session, student_id: str, pet_id: str) -> Pet:
        existing = self.find_owned_model(db, student_id, pet_id)
        pet_dto = Pet.model_validate(existing)

        self.repository.delete(db, existing)
        return pet_dto

    def delete_all_for_student(self, db: Session, student_id: str) -> None:
        self.repository.delete_by_student(db, student_id)

    def find_owned(self, db: Session, student_id: str, pet_id: str) -> Pet:
        pet_model = self.find_owned_model(db, student_id, pet_id)
        return Pet.model_validate(pet_model)

    def find_owned_model(
        self, db: Session, student_id: str, pet_id: str
    ) -> PetModel:
        StudentsService(db).find_by_id(student_id)

        pet = self.repository.find_by_id(db, pet_id)

        if pet is None or pet.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )

        return pet

    def assert_no_conflicts(
        self,
        db: Session,
        student_id: str,
        data: CreatePetDto | UpdatePetDto,
        except_id: str | None = None,
    ) -> None:
        if not data.name:
            return

        existing = self.repository.find_by_student_and_name(db, student_id, data.name)

        if existing and existing.id != except_id:
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            )


pets_service = PetsService(pets_repository)