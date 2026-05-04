"""Use cases for Address listing, update, and deletion."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from dh_shared import Person, Address
from app.contexts.people.application.dtos.people_dto import AddressResponseDTO, UpdateAddressDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class ListAddressesUseCase:
    async def execute(self, uuid_person: str) -> list[AddressResponseDTO]:
        async with AsyncSessionLocal() as session:
            person = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Address).where(Address.id_person == id_person))
            addresses = result.scalars().all()
            return [AddressResponseDTO(
                uuid=a.uuid, type_address=a.type_address, postal_code=a.postal_code,
                key_state=a.key_state, key_municipality=a.key_municipality,
                key_colony=a.key_colony, address=a.address,
                address_complement=a.address_complement,
            ) for a in addresses]


class UpdateAddressUseCase:
    async def execute(self, uuid_person: str, dto: UpdateAddressDTO) -> AddressResponseDTO:
        async with AsyncSessionLocal() as session:
            person_row = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person_row.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Address).where(Address.id_person == id_person).limit(1))
            addr = result.scalar_one_or_none()
            if not addr:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
            if dto.postal_code is not None:
                addr.postal_code = dto.postal_code
            if dto.key_state is not None:
                addr.key_state = dto.key_state
            if dto.key_municipality is not None:
                addr.key_municipality = dto.key_municipality
            if dto.key_colony is not None:
                addr.key_colony = dto.key_colony
            if dto.address is not None:
                addr.address = dto.address
            if dto.address_complement is not None:
                addr.address_complement = dto.address_complement
            if dto.type_address is not None:
                addr.type_address = dto.type_address
            await session.flush()
            await session.refresh(addr)
            await session.commit()
        await logger.event("address_updated", uuid_person=uuid_person)
        return AddressResponseDTO(
            uuid=addr.uuid, type_address=addr.type_address, postal_code=addr.postal_code,
            key_state=addr.key_state, key_municipality=addr.key_municipality,
            key_colony=addr.key_colony, address=addr.address,
            address_complement=addr.address_complement,
        )


class DeleteAddressUseCase:
    async def execute(self, uuid_person: str) -> None:
        async with AsyncSessionLocal() as session:
            person_row = await session.execute(select(Person.id).where(Person.uuid == uuid.UUID(uuid_person)))
            id_person = person_row.scalar_one_or_none()
            if not id_person:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Address).where(Address.id_person == id_person).limit(1))
            addr = result.scalar_one_or_none()
            if not addr:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
            await session.delete(addr)
            await session.commit()
        await logger.event("address_deleted", uuid_person=uuid_person)