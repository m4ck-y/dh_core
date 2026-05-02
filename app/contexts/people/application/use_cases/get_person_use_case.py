"""Get person by UUID use case."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select

from dh_shared import Person

from app.contexts.people.application.dtos.people_dto import PersonResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class GetPersonUseCase:
    async def execute(self, uuid_person: str) -> PersonResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Person).where(Person.uuid == uuid.UUID(uuid_person))
            )
            person = result.scalar_one_or_none()
            if not person:
                await logger.event("person_get_not_found", uuid_person=uuid_person)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")

        await logger.event("person_get", uuid_person=str(person.uuid))
        return PersonResponseDTO(
            uuid=person.uuid,
            first_name=person.first_name,
            last_name=person.last_name,
            verification_status=person.verification_status,
        )
