"""Use cases for PersonalIdentifier operations."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from dh_shared import Person, PersonalIdentifier
from app.contexts.people.application.dtos.people_dto import CreateIdentifierDTO, IdentifierResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreateIdentifierUseCase:
    async def execute(self, uuid_person: str, dto: CreateIdentifierDTO) -> IdentifierResponseDTO:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            person_id = person.scalar_one_or_none()
            if not person_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            ident = PersonalIdentifier(
                id_person=person_id, id_identifier_type=dto.id_identifier_type,
                identifier_value=dto.identifier_value,
            )
            session.add(ident)
            await session.flush()
            await session.refresh(ident)
            await session.commit()
        await logger.event("identifier_created", uuid_person=uuid_person, type=dto.id_identifier_type)
        return IdentifierResponseDTO(uuid=ident.uuid, type=ident.id_identifier_type, value=ident.identifier_value)


class ListIdentifiersUseCase:
    async def execute(self, uuid_person: str) -> list[IdentifierResponseDTO]:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            person_id = person.scalar_one_or_none()
            if not person_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(PersonalIdentifier).where(PersonalIdentifier.id_person == person_id))
            ids = result.scalars().all()
            return [IdentifierResponseDTO(uuid=i.uuid, type=i.id_identifier_type, value=i.identifier_value) for i in ids]
