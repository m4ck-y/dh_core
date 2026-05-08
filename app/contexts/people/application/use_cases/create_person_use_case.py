from dh_shared import Person, Email, Phone, Birth, LegalInfo
from dh_shared import EVerificationStatus

from app.contexts.people.application.dtos.people_dto import CreatePersonDTO, PersonResponseDTO
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.utils.logger import logger


class CreatePersonUseCase:
    async def execute(self, dto: CreatePersonDTO) -> PersonResponseDTO:
        async with AsyncSessionLocal() as session:
            person = Person(
                verification_status=EVerificationStatus.PENDING,
                first_name=dto.first_name,
                last_name=dto.last_name,
                second_last_name=dto.second_last_name,
                type_gender=dto.type_gender,
            )
            session.add(person)
            await session.flush()

            id_person = person.id
            uuid_person = person.uuid

            session.add(Birth(
                id_person=id_person,
                birth_date=dto.birth.date,
                key_birth_country=dto.birth.key_country,
                key_state_birth=dto.birth.key_state,
            ))

            if dto.email:
                session.add(Email(id_person=id_person, email=dto.email.address, type_email=dto.email.type))

            if dto.phone:
                session.add(Phone(id_person=id_person, code=dto.phone.code, number=dto.phone.number, type_phone=dto.phone.type))

            if dto.key_nationality:
                session.add(LegalInfo(id_person=id_person, key_nationality=dto.key_nationality))

            await session.commit()

        await logger.event("person_created", uuid_person=str(uuid_person))

        return PersonResponseDTO(
            uuid=uuid_person,
            first_name=dto.first_name,
            last_name=dto.last_name,
            second_last_name=dto.second_last_name,
            type_gender=dto.type_gender,
            verification_status=EVerificationStatus.PENDING,
        )
