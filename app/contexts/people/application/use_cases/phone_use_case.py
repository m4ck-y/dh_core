"""Use cases for Phone operations. Get/Update/Delete operate by uuid_phone (ADR 034)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Person, Phone
from dh_shared.queries import resolve_uuid_to_id
from app.contexts.people.application.dtos.people_dto import CreatePhoneDTO, PhoneResponseDTO, UpdatePhoneDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(p: Phone) -> PhoneResponseDTO:
    return PhoneResponseDTO(uuid=p.uuid, code=p.code, number=p.number, type_phone=p.type_phone)


class CreatePhoneUseCase:
    async def execute(self, uuid_person: str, dto: CreatePhoneDTO) -> PhoneResponseDTO:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            phone = Phone(id_person=id_person, code=dto.code, number=dto.number, type_phone=dto.type_phone)
            session.add(phone)
            await session.flush()
            await session.refresh(phone)
            await session.commit()
        await logger.event("phone_created", uuid_person=uuid_person, number=dto.number)
        return _to_dto(phone)


class ListPhonesUseCase:
    async def execute(self, uuid_person: str) -> list[PhoneResponseDTO]:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Phone).where(Phone.id_person == id_person))
            return [_to_dto(p) for p in result.scalars().all()]


class GetPhoneUseCase:
    async def execute(self, uuid_phone: str) -> PhoneResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Phone).where(Phone.uuid == uuid.UUID(uuid_phone)))
            phone = result.scalar_one_or_none()
            if not phone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")
            return _to_dto(phone)


class UpdatePhoneUseCase:
    async def execute(self, uuid_phone: str, dto: UpdatePhoneDTO) -> PhoneResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Phone).where(Phone.uuid == uuid.UUID(uuid_phone)))
            phone = result.scalar_one_or_none()
            if not phone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")
            if dto.code is not None:
                phone.code = dto.code
            if dto.number is not None:
                phone.number = dto.number
            if dto.type_phone is not None:
                phone.type_phone = dto.type_phone
            await session.flush()
            await session.refresh(phone)
            await session.commit()
        await logger.event("phone_updated", uuid_phone=uuid_phone)
        return _to_dto(phone)


class DeletePhoneUseCase:
    async def execute(self, uuid_phone: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Phone).where(Phone.uuid == uuid.UUID(uuid_phone)))
            phone = result.scalar_one_or_none()
            if not phone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")
            await session.delete(phone)
            await session.commit()
        await logger.event("phone_deleted", uuid_phone=uuid_phone)
