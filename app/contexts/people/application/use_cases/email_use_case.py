"""Use cases for Email operations. Get/Update/Delete operate by uuid_email (ADR 034)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Person, Email
from dh_shared.queries import resolve_uuid_to_id
from app.contexts.people.application.dtos.people_dto import CreateEmailDTO, EmailResponseDTO, UpdateEmailDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(e: Email) -> EmailResponseDTO:
    return EmailResponseDTO(uuid=e.uuid, email=e.email, type_email=e.type_email)


class CreateEmailUseCase:
    async def execute(self, uuid_person: str, dto: CreateEmailDTO) -> EmailResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            email = Email(id_person=id_person, email=dto.email, type_email=dto.type_email)
            session.add(email)
            await session.flush()
            await session.refresh(email)
            await session.commit()
        await logger.event("email_created", uuid_person=uuid_person, email=dto.email)
        return _to_dto(email)


class ListEmailsUseCase:
    async def execute(self, uuid_person: str) -> list[EmailResponseDTO]:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Email).where(Email.id_person == id_person))
            return [_to_dto(e) for e in result.scalars().all()]


class GetEmailUseCase:
    async def execute(self, uuid_email: str) -> EmailResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Email).where(Email.uuid == uuid.UUID(uuid_email)))
            email = result.scalar_one_or_none()
            if not email:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
            return _to_dto(email)


class UpdateEmailUseCase:
    async def execute(self, uuid_email: str, dto: UpdateEmailDTO) -> EmailResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Email).where(Email.uuid == uuid.UUID(uuid_email)))
            email = result.scalar_one_or_none()
            if not email:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
            if dto.email is not None:
                email.email = dto.email
            if dto.type_email is not None:
                email.type_email = dto.type_email
            await session.flush()
            await session.refresh(email)
            await session.commit()
        await logger.event("email_updated", uuid_email=uuid_email)
        return _to_dto(email)


class DeleteEmailUseCase:
    async def execute(self, uuid_email: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Email).where(Email.uuid == uuid.UUID(uuid_email)))
            email = result.scalar_one_or_none()
            if not email:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
            await session.delete(email)
            await session.commit()
        await logger.event("email_deleted", uuid_email=uuid_email)
