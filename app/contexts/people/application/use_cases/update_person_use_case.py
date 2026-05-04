"""Update person mutable fields use case."""

import uuid
from datetime import timezone, datetime

from fastapi import HTTPException, status
from sqlalchemy import select

from dh_shared import Person

from app.contexts.people.application.dtos.people_dto import UpdatePersonDTO, PersonResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class UpdatePersonUseCase:
    async def execute(self, uuid_person: str, dto: UpdatePersonDTO) -> PersonResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Person).where(Person.uuid == uuid.UUID(uuid_person))
            )
            person = result.scalar_one_or_none()
            if not person:
                await logger.event("person_update_not_found", uuid_person=uuid_person)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")

            if dto.first_name is not None:
                person.first_name = dto.first_name
            if dto.last_name is not None:
                person.last_name = dto.last_name
            if dto.second_last_name is not None:
                person.second_last_name = dto.second_last_name
            if dto.type_gender is not None:
                person.type_gender = dto.type_gender
            if dto.verification_status is not None:
                person.verification_status = dto.verification_status

            person.updated_at = datetime.now(timezone.utc)
            await session.flush()
            await session.refresh(person)
            await session.commit()

        await logger.event("person_updated", uuid_person=uuid_person)
        return PersonResponseDTO(
            uuid=person.uuid,
            first_name=person.first_name,
            last_name=person.last_name,
            second_last_name=person.second_last_name,
            type_gender=person.type_gender,
            verification_status=person.verification_status,
        )
