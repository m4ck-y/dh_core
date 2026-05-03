"""Use cases for EmergencyContact operations."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from dh_shared import Person, EmergencyContact
from app.contexts.people.application.dtos.people_dto import CreateEmergencyContactDTO, EmergencyContactResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreateEmergencyContactUseCase:
    async def execute(self, uuid_person: str, dto: CreateEmergencyContactDTO) -> EmergencyContactResponseDTO:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            ec = EmergencyContact(
                id_user_owner=id_person, relationship_type=dto.relationship_type,
                first_name=dto.first_name, last_name=dto.last_name,
                phone_number=dto.phone_number, email=dto.email, notes=dto.notes,
            )
            session.add(ec)
            await session.flush()
            await session.refresh(ec)
            await session.commit()
        await logger.event("emergency_contact_created", uuid_person=uuid_person)
        return EmergencyContactResponseDTO(
            uuid=ec.uuid, first_name=ec.first_name, last_name=ec.last_name,
            phone_number=ec.phone_number, relationship_type=ec.relationship_type,
        )


class ListEmergencyContactsUseCase:
    async def execute(self, uuid_person: str) -> list[EmergencyContactResponseDTO]:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.id_user_owner == id_person))
            contacts = result.scalars().all()
            return [EmergencyContactResponseDTO(
                uuid=c.uuid, first_name=c.first_name, last_name=c.last_name,
                phone_number=c.phone_number, relationship_type=c.relationship_type,
            ) for c in contacts]
