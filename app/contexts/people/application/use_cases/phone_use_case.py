"""Use cases for Phone operations on a person."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from dh_shared import Person, Phone
from app.contexts.people.application.dtos.people_dto import CreatePhoneDTO, PhoneResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreatePhoneUseCase:
    async def execute(self, uuid_person: str, dto: CreatePhoneDTO) -> PhoneResponseDTO:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            phone = Phone(id_person=id_person, code=dto.code, number=dto.number, type_phone=dto.type_phone)
            session.add(phone)
            await session.flush()
            await session.refresh(phone)
            await session.commit()
        await logger.event("phone_created", uuid_person=uuid_person, number=dto.number)
        return PhoneResponseDTO(uuid=phone.uuid, code=phone.code, number=phone.number, type_phone=phone.type_phone)


class ListPhonesUseCase:
    async def execute(self, uuid_person: str) -> list[PhoneResponseDTO]:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Phone).where(Phone.id_person == id_person))
            phones = result.scalars().all()
            return [PhoneResponseDTO(uuid=p.uuid, code=p.code, number=p.number, type_phone=p.type_phone) for p in phones]
