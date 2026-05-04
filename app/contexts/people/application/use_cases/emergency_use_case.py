"""Use cases for EmergencyContact operations."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from dh_shared import Person, EmergencyContact
from app.contexts.people.application.dtos.people_dto import CreateEmergencyContactDTO, EmergencyContactResponseDTO, UpdateEmergencyContactDTO
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
                phone_number=c.phone_number, email=c.email,
                relationship_type=c.relationship_type, notes=c.notes,
            ) for c in contacts]


class UpdateEmergencyContactUseCase:
    async def execute(self, uuid_person: str, dto: UpdateEmergencyContactDTO) -> EmergencyContactResponseDTO:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.id_user_owner == id_person).limit(1))
            ec = result.scalar_one_or_none()
            if not ec:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")
            if dto.first_name is not None:
                ec.first_name = dto.first_name
            if dto.last_name is not None:
                ec.last_name = dto.last_name
            if dto.phone_number is not None:
                ec.phone_number = dto.phone_number
            if dto.email is not None:
                ec.email = dto.email
            if dto.relationship_type is not None:
                ec.relationship_type = dto.relationship_type
            if dto.notes is not None:
                ec.notes = dto.notes
            await session.flush()
            await session.refresh(ec)
            await session.commit()
        await logger.event("emergency_contact_updated", uuid_person=uuid_person)
        return EmergencyContactResponseDTO(
            uuid=ec.uuid, first_name=ec.first_name, last_name=ec.last_name,
            phone_number=ec.phone_number, email=ec.email,
            relationship_type=ec.relationship_type, notes=ec.notes,
        )


class DeleteEmergencyContactUseCase:
    async def execute(self, uuid_person: str) -> None:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.id_user_owner == id_person).limit(1))
            ec = result.scalar_one_or_none()
            if not ec:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")
            await session.delete(ec)
            await session.commit()
        await logger.event("emergency_contact_deleted", uuid_person=uuid_person)
