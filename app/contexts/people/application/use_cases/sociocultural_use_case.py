"""Use cases for SocioculturalIdentity (1:1 with Person). Operations use uuid_person (ADR 034 exception for 1:1)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import SocioculturalIdentity
from dh_shared.queries import resolve_uuid_to_id
from dh_shared.models.people.person import Person
from app.contexts.people.application.dtos.people_dto import SocioculturalResponseDTO, CreateSocioculturalDTO, UpdateSocioculturalDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(s: SocioculturalIdentity) -> SocioculturalResponseDTO:
    return SocioculturalResponseDTO(
        uuid=s.uuid,
        self_considers_indigenous=s.self_considers_indigenous,
        key_indigenous_language=s.key_indigenous_language,
        self_considers_migrant=s.self_considers_migrant,
        key_country_origin=s.key_country_origin,
        key_religion=s.key_religion,
        religion_other=s.religion_other,
    )


class GetSocioculturalUseCase:
    async def execute(self, uuid_person: str) -> SocioculturalResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(SocioculturalIdentity).where(SocioculturalIdentity.id_person == id_person))
            sc = result.scalar_one_or_none()
            if not sc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sociocultural identity not found.")
            return _to_dto(sc)


class CreateSocioculturalUseCase:
    async def execute(self, uuid_person: str, dto: CreateSocioculturalDTO) -> SocioculturalResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            existing = (await session.execute(select(SocioculturalIdentity).where(SocioculturalIdentity.id_person == id_person))).scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sociocultural identity already exists. Use PATCH to update.")
            sc = SocioculturalIdentity(
                id_person=id_person,
                self_considers_indigenous=dto.self_considers_indigenous,
                key_indigenous_language=dto.key_indigenous_language,
                self_considers_migrant=dto.self_considers_migrant,
                key_country_origin=dto.key_country_origin,
                key_religion=dto.key_religion,
                religion_other=dto.religion_other,
            )
            session.add(sc)
            await session.flush()
            await session.refresh(sc)
            await session.commit()
        await logger.event("sociocultural_created", uuid_person=uuid_person)
        return _to_dto(sc)


class UpdateSocioculturalUseCase:
    async def execute(self, uuid_person: str, dto: UpdateSocioculturalDTO) -> SocioculturalResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(SocioculturalIdentity).where(SocioculturalIdentity.id_person == id_person))
            sc = result.scalar_one_or_none()
            if not sc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sociocultural identity not found. Use POST to create.")
            for field in ("self_considers_indigenous", "key_indigenous_language", "self_considers_migrant", "key_country_origin", "key_religion", "religion_other"):
                val = getattr(dto, field, None)
                if val is not None:
                    setattr(sc, field, val)
            await session.flush()
            await session.refresh(sc)
            await session.commit()
        await logger.event("sociocultural_updated", uuid_person=uuid_person)
        return _to_dto(sc)
