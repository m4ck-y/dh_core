"""Use case for checking if a person already exists by email, personal identifier, or phone."""

from typing import Optional

from app.contexts.people.application.dtos.people_dto import PersonExistsResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger
from dh_shared.queries import check_conflicts, find_person_by_email_or_identifier


class CheckPersonExistsUseCase:
    """Check which fields are already registered. UUIDs logged internally, never returned."""

    async def execute(
        self,
        email: Optional[str] = None,
        personal_id: Optional[str] = None,
        phone_code: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> PersonExistsResponseDTO:
        async with AsyncSessionLocal() as session:
            conflicts = await check_conflicts(
                session,
                email=email,
                personal_id=personal_id,
                phone_code=phone_code,
                phone_number=phone_number,
            )

            if any(conflicts.values()):
                person_row = await find_person_by_email_or_identifier(session, email=email, personal_id=personal_id)
                uuid_existing = str(person_row[1]) if person_row else None
                await logger.event(
                    "registration_conflict",
                    uuid_person=uuid_existing,
                    email=email if conflicts["email_already_registered"] else None,
                    personal_id=personal_id if conflicts["personal_id_already_registered"] else None,
                )

            return PersonExistsResponseDTO(**conflicts)
