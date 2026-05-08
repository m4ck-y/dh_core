"""Use cases for Profile (1:1 with Person). Operations use uuid_person (ADR 034 exception for 1:1)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Profile
from dh_shared.queries import resolve_uuid_to_id
from dh_shared.models.people.person import Person
from app.contexts.people.application.dtos.people_dto import ProfileResponseDTO, CreateProfileDTO, UpdateProfileDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(p: Profile) -> ProfileResponseDTO:
    return ProfileResponseDTO(
        uuid=p.uuid, occupation_type=p.occupation_type, occupation_other=p.occupation_other,
        known_as=p.known_as, education_level=p.education_level,
        income_range=p.income_range, about_me=p.about_me,
    )


class GetProfileUseCase:
    async def execute(self, uuid_person: str) -> ProfileResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Profile).where(Profile.id_person == id_person))
            profile = result.scalar_one_or_none()
            if not profile:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
            return _to_dto(profile)


class CreateProfileUseCase:
    async def execute(self, uuid_person: str, dto: CreateProfileDTO) -> ProfileResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            existing = (await session.execute(select(Profile).where(Profile.id_person == id_person))).scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists. Use PATCH to update.")
            profile = Profile(
                id_person=id_person,
                occupation_type=dto.occupation_type, occupation_other=dto.occupation_other,
                known_as=dto.known_as, education_level=dto.education_level,
                income_range=dto.income_range, about_me=dto.about_me,
            )
            session.add(profile)
            await session.flush()
            await session.refresh(profile)
            await session.commit()
        await logger.event("profile_created", uuid_person=uuid_person)
        return _to_dto(profile)


class UpdateProfileUseCase:
    async def execute(self, uuid_person: str, dto: UpdateProfileDTO) -> ProfileResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Profile).where(Profile.id_person == id_person))
            profile = result.scalar_one_or_none()
            if not profile:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found. Use POST to create.")
            for field in ("occupation_type", "occupation_other", "known_as", "education_level", "income_range", "about_me"):
                val = getattr(dto, field, None)
                if val is not None:
                    setattr(profile, field, val)
            await session.flush()
            await session.refresh(profile)
            await session.commit()
        await logger.event("profile_updated", uuid_person=uuid_person)
        return _to_dto(profile)
