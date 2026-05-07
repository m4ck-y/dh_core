"""Use cases for Address operations. Get/Update/Delete operate by uuid_address (ADR 034)."""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from dh_shared import Person, Address
from dh_shared.queries import resolve_uuid_to_id
from app.contexts.people.application.dtos.people_dto import AddressResponseDTO, UpdateAddressDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


def _to_dto(a: Address) -> AddressResponseDTO:
    return AddressResponseDTO(
        uuid=a.uuid, type_address=a.type_address, postal_code=a.postal_code,
        key_state=a.key_state, key_municipality=a.key_municipality,
        key_colony=a.key_colony, address=a.address,
        address_complement=a.address_complement,
    )


class ListAddressesUseCase:
    async def execute(self, uuid_person: str) -> list[AddressResponseDTO]:
        async with AsyncSessionLocal() as session:
            try:
                id_person = await resolve_uuid_to_id(session, Person, uuid.UUID(uuid_person))
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")
            result = await session.execute(select(Address).where(Address.id_person == id_person))
            return [_to_dto(a) for a in result.scalars().all()]


class GetAddressUseCase:
    async def execute(self, uuid_address: str) -> AddressResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Address).where(Address.uuid == uuid.UUID(uuid_address)))
            addr = result.scalar_one_or_none()
            if not addr:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
            return _to_dto(addr)


class UpdateAddressUseCase:
    async def execute(self, uuid_address: str, dto: UpdateAddressDTO) -> AddressResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Address).where(Address.uuid == uuid.UUID(uuid_address)))
            addr = result.scalar_one_or_none()
            if not addr:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
            for field in ("postal_code", "key_state", "key_municipality", "key_colony", "address", "address_complement", "type_address"):
                val = getattr(dto, field, None)
                if val is not None:
                    setattr(addr, field, val)
            await session.flush()
            await session.refresh(addr)
            await session.commit()
        await logger.event("address_updated", uuid_address=uuid_address)
        return _to_dto(addr)


class DeleteAddressUseCase:
    async def execute(self, uuid_address: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Address).where(Address.uuid == uuid.UUID(uuid_address)))
            addr = result.scalar_one_or_none()
            if not addr:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
            await session.delete(addr)
            await session.commit()
        await logger.event("address_deleted", uuid_address=uuid_address)
