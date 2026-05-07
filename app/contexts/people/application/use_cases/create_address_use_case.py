import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound

from dh_shared import Address, Person
from dh_shared.queries import resolve_uuid_to_id

from app.contexts.people.application.dtos.people_dto import CreateAddressDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreateAddressUseCase:
    async def execute(self, uuid_person: str, dto: CreateAddressDTO) -> None:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
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
