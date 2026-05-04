"""List persons with pagination use case."""

import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func

from dh_shared import Person

from app.contexts.people.application.dtos.people_dto import PersonResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class ListPersonsUseCase:
    async def execute(self, page: int = 1, limit: int = 50) -> tuple[list[PersonResponseDTO], int, int]:
        offset = (page - 1) * limit
        async with AsyncSessionLocal() as session:
            total_result = await session.execute(
                select(func.count(Person.id))
            )
            total = total_result.scalar_one()
            pages = max(1, math.ceil(total / limit))
            result = await session.execute(
                select(Person).offset(offset).limit(limit)
            )
            persons = result.scalars().all()
        await logger.event("persons_listed", page=page, limit=limit, total=total)
        return (
            [
                PersonResponseDTO(
                    uuid=p.uuid,
                    first_name=p.first_name,
                    last_name=p.last_name,
                    second_last_name=p.second_last_name,
                    type_gender=p.type_gender,
                    verification_status=p.verification_status,
                )
                for p in persons
            ],
            total,
            pages,
        )
