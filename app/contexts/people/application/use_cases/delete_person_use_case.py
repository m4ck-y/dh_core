"""Soft-delete person use case."""

import uuid
from datetime import timezone, datetime

from fastapi import HTTPException, status
from sqlalchemy import select

from dh_shared import Person

from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class DeletePersonUseCase:
    async def execute(self, uuid_person: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Person).where(Person.uuid == uuid.UUID(uuid_person))
            )
            person = result.scalar_one_or_none()
            if not person:
                await logger.event("person_delete_not_found", uuid_person=uuid_person)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")

            person.deleted_at = datetime.now(timezone.utc)
            await session.flush()
            await session.commit()

        await logger.event("person_deleted", uuid_person=uuid_person)
