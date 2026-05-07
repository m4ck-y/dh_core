"""Use cases for PersonalIdentifier operations. Get/Update/Delete operate by uuid_identifier (ADR 034)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Person, PersonalIdentifier
from dh_shared.queries import resolve_uuid_to_id
from app.contexts.people.application.dtos.people_dto import CreateIdentifierDTO, IdentifierResponseDTO, UpdateIdentifierDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(i: PersonalIdentifier) -> IdentifierResponseDTO:
    return IdentifierResponseDTO(uuid=i.uuid, type=i.id_identifier_type, value=i.identifier_value)


class CreateIdentifierUseCase:
    async def execute(self, uuid_person: str, dto: CreateIdentifierDTO) -> IdentifierResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            ident = PersonalIdentifier(
                id_person=id_person, id_identifier_type=dto.id_identifier_type,
                identifier_value=dto.identifier_value,
            )
            session.add(ident)
            await session.flush()
            await session.refresh(ident)
            await session.commit()
        await logger.event("identifier_created", uuid_person=uuid_person, type=dto.id_identifier_type)
        return _to_dto(ident)


class ListIdentifiersUseCase:
    async def execute(self, uuid_person: str) -> list[IdentifierResponseDTO]:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(PersonalIdentifier).where(PersonalIdentifier.id_person == id_person))
            return [_to_dto(i) for i in result.scalars().all()]


class GetIdentifierUseCase:
    async def execute(self, uuid_identifier: str) -> IdentifierResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(PersonalIdentifier).where(PersonalIdentifier.uuid == uuid.UUID(uuid_identifier)))
            ident = result.scalar_one_or_none()
            if not ident:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identifier not found.")
            return _to_dto(ident)


class UpdateIdentifierUseCase:
    async def execute(self, uuid_identifier: str, dto: UpdateIdentifierDTO) -> IdentifierResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(PersonalIdentifier).where(PersonalIdentifier.uuid == uuid.UUID(uuid_identifier)))
            ident = result.scalar_one_or_none()
            if not ident:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identifier not found.")
            if dto.id_identifier_type is not None:
                ident.id_identifier_type = dto.id_identifier_type
            if dto.identifier_value is not None:
                ident.identifier_value = dto.identifier_value
            await session.flush()
            await session.refresh(ident)
            await session.commit()
        await logger.event("identifier_updated", uuid_identifier=uuid_identifier)
        return _to_dto(ident)


class DeleteIdentifierUseCase:
    async def execute(self, uuid_identifier: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(PersonalIdentifier).where(PersonalIdentifier.uuid == uuid.UUID(uuid_identifier)))
            ident = result.scalar_one_or_none()
            if not ident:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identifier not found.")
            await session.delete(ident)
            await session.commit()
        await logger.event("identifier_deleted", uuid_identifier=uuid_identifier)
