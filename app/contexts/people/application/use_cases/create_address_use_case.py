import uuid

from fastapi import HTTPException, status
from sqlalchemy import select

from dh_shared import Address, Person

from app.contexts.people.application.dtos.people_dto import CreateAddressDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreateAddressUseCase:
    async def execute(self, uuid_person: str, dto: CreateAddressDTO) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Person.id).where(Person.uuid == uuid.UUID(uuid_person))
            )
            id_person = result.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")

            session.add(Address(
                id_person=id_person,
                type_address=dto.type_address,
                postal_code=dto.postal_code,
                key_state=dto.key_state,
                key_municipality=dto.key_municipality,
                key_colony=dto.key_colony,
                address=dto.address,
                address_complement=dto.address_complement,
            ))
            await session.commit()
        await logger.event("address_created", uuid_person=uuid_person)
