"""Use cases for Email operations on a person."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from dh_shared import Person, Email
from app.contexts.people.application.dtos.people_dto import CreateEmailDTO, EmailResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreateEmailUseCase:
    async def execute(self, uuid_person: str, dto: CreateEmailDTO) -> EmailResponseDTO:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            person_id = person.scalar_one_or_none()
            if not person_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            email = Email(id_person=person_id, email=dto.email, type_email=dto.type_email)
            session.add(email)
            await session.flush()
            await session.refresh(email)
            await session.commit()
        await logger.event("email_created", uuid_person=uuid_person, email=dto.email)
        return EmailResponseDTO(uuid=email.uuid, email=email.email, type_email=email.type_email)


class ListEmailsUseCase:
    async def execute(self, uuid_person: str) -> list[EmailResponseDTO]:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            person_id = person.scalar_one_or_none()
            if not person_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Email).where(Email.id_person == person_id))
            emails = result.scalars().all()
            return [EmailResponseDTO(uuid=e.uuid, email=e.email, type_email=e.type_email) for e in emails]
