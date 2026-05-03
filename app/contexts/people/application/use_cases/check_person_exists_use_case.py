"""Use case for checking if a person already exists by email or CURP."""

from typing import Optional
from sqlalchemy import select

from dh_shared.models.people import Person, Email, PersonalIdentifier
from app.contexts.people.application.dtos.people_dto import PersonExistsResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CheckPersonExistsUseCase:
    """Check if person exists by email or CURP."""

    async def by_email(self, email: str) -> PersonExistsResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Person.uuid)
                .join(Email, Email.id_person == Person.id)
                .where(Email.email == email)
            )
            person_data = result.first()
            if person_data:
                await logger.event("person_check_by_email", email=email, found=True)
                return PersonExistsResponseDTO(exists=True, uuid_person=str(person_data.uuid))
            await logger.event("person_check_by_email", email=email, found=False)
            return PersonExistsResponseDTO(exists=False)

    async def by_curp(self, curp: str) -> PersonExistsResponseDTO:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Person.uuid)
                .join(PersonalIdentifier, PersonalIdentifier.id_person == Person.id)
                .where(PersonalIdentifier.identifier_value == curp.upper())
            )
            person_data = result.first()
            if person_data:
                await logger.event("person_check_by_curp", curp=curp, found=True)
                return PersonExistsResponseDTO(exists=True, uuid_person=str(person_data.uuid))
            await logger.event("person_check_by_curp", curp=curp, found=False)
            return PersonExistsResponseDTO(exists=False)

    async def by_email_or_curp(self, email: str, curp: Optional[str] = None) -> PersonExistsResponseDTO:
        email_result = await self.by_email(email)
        if email_result.exists:
            return email_result
        if curp:
            return await self.by_curp(curp)
        return PersonExistsResponseDTO(exists=False)
