from sqlalchemy.orm import Session
from app.pets.pets_model import Pet


class PetsRepository:
    def find_all_by_student(self, db: Session, student_id: str) -> list[Pet]:
        return db.query(Pet).filter(Pet.student_id == student_id).all()

    def find_by_id(self, db: Session, pet_id: str) -> Pet | None:
        return db.query(Pet).filter(Pet.id == pet_id).first()

    def find_by_student_and_name(
        self, db: Session, student_id: str, name: str
    ) -> Pet | None:
        return (
            db.query(Pet)
            .filter(Pet.student_id == student_id, Pet.name == name)
            .first()
        )

    def save(self, db: Session, pet: Pet) -> Pet:
        db.add(pet)
        db.commit()
        db.refresh(pet)
        return pet

    def delete(self, db: Session, pet: Pet) -> None:
        db.delete(pet)
        db.commit()

    def delete_by_student(self, db: Session, student_id: str) -> None:
        db.query(Pet).filter(Pet.student_id == student_id).delete()
        db.commit()


pets_repository = PetsRepository()