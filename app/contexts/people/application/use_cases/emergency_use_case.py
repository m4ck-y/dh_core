"""Use cases for EmergencyContact operations. Get/Update/Delete operate by uuid_emergency (ADR 034)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Person, EmergencyContact
from dh_shared.queries import resolve_uuid_to_id
from app.contexts.people.application.dtos.people_dto import CreateEmergencyContactDTO, EmergencyContactResponseDTO, UpdateEmergencyContactDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(c: EmergencyContact) -> EmergencyContactResponseDTO:
    return EmergencyContactResponseDTO(
        uuid=c.uuid, first_name=c.first_name, last_name=c.last_name,
        phone_number=c.phone_number, email=c.email,
        relationship_type=c.relationship_type, notes=c.notes,
    )


class CreateEmergencyContactUseCase:
    async def execute(self, uuid_person: str, dto: CreateEmergencyContactDTO) -> EmergencyContactResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
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
        return _to_dto(ec)


class ListEmergencyContactsUseCase:
    async def execute(self, uuid_person: str) -> list[EmergencyContactResponseDTO]:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.id_user_owner == id_person))
            return [_to_dto(c) for c in result.scalars().all()]


class GetEmergencyContactUseCase:
    async def execute(self, uuid_emergency: str) -> EmergencyContactResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.uuid == uuid.UUID(uuid_emergency)))
            ec = result.scalar_one_or_none()
            if not ec:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")
            return _to_dto(ec)


class UpdateEmergencyContactUseCase:
    async def execute(self, uuid_emergency: str, dto: UpdateEmergencyContactDTO) -> EmergencyContactResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.uuid == uuid.UUID(uuid_emergency)))
            ec = result.scalar_one_or_none()
            if not ec:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")
            for field in ("first_name", "last_name", "phone_number", "email", "relationship_type", "notes"):
                val = getattr(dto, field, None)
                if val is not None:
                    setattr(ec, field, val)
            await session.flush()
            await session.refresh(ec)
            await session.commit()
        await logger.event("emergency_contact_updated", uuid_emergency=uuid_emergency)
        return _to_dto(ec)


class DeleteEmergencyContactUseCase:
    async def execute(self, uuid_emergency: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(EmergencyContact).where(EmergencyContact.uuid == uuid.UUID(uuid_emergency)))
            ec = result.scalar_one_or_none()
            if not ec:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")
            await session.delete(ec)
            await session.commit()
        await logger.event("emergency_contact_deleted", uuid_emergency=uuid_emergency)
