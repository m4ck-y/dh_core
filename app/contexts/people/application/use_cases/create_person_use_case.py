from dh_shared import Person, Email, Phone, Birth, LegalInfo, PersonalIdentifier
from dh_shared import EEmailType, EIdentifierType, EPhoneType, EVerificationStatus

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

            session.add(Email(id_person=id_person, email=dto.email, type_email=EEmailType.PERSONAL))
            session.add(Phone(id_person=id_person, code=dto.phone_code, number=dto.phone_number, type_phone=EPhoneType.MOBILE))
            session.add(Birth(
                id_person=id_person,
                birth_date=dto.birth_date,
                key_birth_country=dto.key_birth_country,
                key_state_birth=dto.key_birth_state,
            ))

            if dto.key_nationality:
                session.add(LegalInfo(id_person=id_person, key_nationality=dto.key_nationality))

            if dto.personal_identifier and dto.personal_identifier.value:
                session.add(PersonalIdentifier(
                    id_person=id_person,
                    id_identifier_type=dto.personal_identifier.type,
                    identifier_value=dto.personal_identifier.value,
                ))

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
