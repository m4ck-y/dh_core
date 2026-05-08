"""Use cases for Birth (1:1 with Person). Operations use uuid_person (ADR 034 exception for 1:1)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Birth
from dh_shared.queries import resolve_uuid_to_id
from dh_shared.models.people.person import Person
from app.contexts.people.application.dtos.people_dto import BirthResponseDTO, UpdateBirthDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(b: Birth) -> BirthResponseDTO:
    return BirthResponseDTO(
        uuid=b.uuid, birth_date=b.birth_date,
        key_birth_country=b.key_birth_country,
        key_state_birth=b.key_state_birth,
        birth_date_timezone=b.birth_date_timezone,
    )


class GetBirthUseCase:
    async def execute(self, uuid_person: str) -> BirthResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Birth).where(Birth.id_person == id_person))
            birth = result.scalar_one_or_none()
            if not birth:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birth record not found.")
            return _to_dto(birth)


class UpdateBirthUseCase:
    async def execute(self, uuid_person: str, dto: UpdateBirthDTO) -> BirthResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Birth).where(Birth.id_person == id_person))
            birth = result.scalar_one_or_none()
            if not birth:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birth record not found.")
            for field in ("birth_date", "key_birth_country", "key_state_birth", "birth_date_timezone"):
                val = getattr(dto, field, None)
                if val is not None:
                    setattr(birth, field, val)
            await session.flush()
            await session.refresh(birth)
            await session.commit()
        await logger.event("birth_updated", uuid_person=uuid_person)
        return _to_dto(birth)
