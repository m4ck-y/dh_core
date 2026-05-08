"""Use cases for LegalInfo (1:1 with Person). Operations use uuid_person (ADR 034 exception for 1:1)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import LegalInfo
from dh_shared.queries import resolve_uuid_to_id
from dh_shared.models.people.person import Person
from app.contexts.people.application.dtos.people_dto import LegalInfoResponseDTO, CreateLegalInfoDTO, UpdateLegalInfoDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(l: LegalInfo) -> LegalInfoResponseDTO:
    return LegalInfoResponseDTO(
        uuid=l.uuid, key_nationality=l.key_nationality,
        type_national_id_sex=l.type_national_id_sex, civil_status=l.civil_status,
    )


class GetLegalInfoUseCase:
    async def execute(self, uuid_person: str) -> LegalInfoResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(LegalInfo).where(LegalInfo.id_person == id_person))
            info = result.scalar_one_or_none()
            if not info:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal info not found.")
            return _to_dto(info)


class CreateLegalInfoUseCase:
    async def execute(self, uuid_person: str, dto: CreateLegalInfoDTO) -> LegalInfoResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            existing = (await session.execute(select(LegalInfo).where(LegalInfo.id_person == id_person))).scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Legal info already exists. Use PATCH to update.")
            info = LegalInfo(
                id_person=id_person,
                key_nationality=dto.key_nationality,
                type_national_id_sex=dto.type_national_id_sex,
                civil_status=dto.civil_status,
            )
            session.add(info)
            await session.flush()
            await session.refresh(info)
            await session.commit()
        await logger.event("legal_info_created", uuid_person=uuid_person)
        return _to_dto(info)


class UpdateLegalInfoUseCase:
    async def execute(self, uuid_person: str, dto: UpdateLegalInfoDTO) -> LegalInfoResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(LegalInfo).where(LegalInfo.id_person == id_person))
            info = result.scalar_one_or_none()
            if not info:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal info not found. Use POST to create.")
            for field in ("key_nationality", "type_national_id_sex", "civil_status"):
                val = getattr(dto, field, None)
                if val is not None:
                    setattr(info, field, val)
            await session.flush()
            await session.refresh(info)
            await session.commit()
        await logger.event("legal_info_updated", uuid_person=uuid_person)
        return _to_dto(info)
