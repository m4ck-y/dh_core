import uuid

from fastapi import HTTPException, status
from sqlalchemy import update

from dh_shared import Person

from app.contexts.people.application.dtos.people_dto import UpdatePersonStatusDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class UpdatePersonStatusUseCase:
    async def execute(self, uuid_person: str, dto: UpdatePersonStatusDTO) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(Person)
                .where(Person.uuid == uuid.UUID(uuid_person))
                .values(verification_status=dto.verification_status)
                .returning(Person.id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            await session.commit()
        await logger.event("person_status_updated", uuid_person=uuid_person, verification_status=dto.verification_status)
