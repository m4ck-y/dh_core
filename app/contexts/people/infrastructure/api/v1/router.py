"""
People endpoints for the Digital Hospital ecosystem.

Owns the `people` schema: Person, Email, Phone, Address, PersonalIdentifier,
Birth, LegalInfo, Profile, SocialPlatform, SocialLinks, EmergencyContact.

Path convention (ADR 034):
  Collection  → /people/{uuid_person}/<resource>       GET list + POST create
  Entity      → /people/<resource>/{uuid_entity}       GET single + PATCH + DELETE
"""

from typing import Optional

from fastapi import APIRouter, Query, status, HTTPException

from app.contexts.people.application.dtos.people_dto import (
    CreatePersonDTO, PersonResponseDTO,
    CreateAddressDTO, UpdateAddressDTO, AddressResponseDTO,
    UpdatePersonStatusDTO, UpdatePersonDTO, PersonExistsResponseDTO,
    CreateEmailDTO, EmailResponseDTO, UpdateEmailDTO,
    CreatePhoneDTO, PhoneResponseDTO, UpdatePhoneDTO,
    CreateIdentifierDTO, IdentifierResponseDTO, UpdateIdentifierDTO,
    CreateEmergencyContactDTO, EmergencyContactResponseDTO, UpdateEmergencyContactDTO,
)
from app.contexts.people.application.use_cases.create_person_use_case import CreatePersonUseCase
from app.contexts.people.application.use_cases.get_person_use_case import GetPersonUseCase
from app.contexts.people.application.use_cases.list_persons_use_case import ListPersonsUseCase
from app.contexts.people.application.use_cases.update_person_use_case import UpdatePersonUseCase
from app.contexts.people.application.use_cases.delete_person_use_case import DeletePersonUseCase
from app.contexts.people.application.use_cases.create_address_use_case import CreateAddressUseCase
from app.contexts.people.application.use_cases.update_person_status_use_case import UpdatePersonStatusUseCase
from app.contexts.people.application.use_cases.check_person_exists_use_case import CheckPersonExistsUseCase
from app.contexts.people.application.use_cases.address_use_case import (
    ListAddressesUseCase, GetAddressUseCase, UpdateAddressUseCase, DeleteAddressUseCase,
)
from app.contexts.people.application.use_cases.email_use_case import (
    CreateEmailUseCase, ListEmailsUseCase, GetEmailUseCase, UpdateEmailUseCase, DeleteEmailUseCase,
)
from app.contexts.people.application.use_cases.phone_use_case import (
    CreatePhoneUseCase, ListPhonesUseCase, GetPhoneUseCase, UpdatePhoneUseCase, DeletePhoneUseCase,
)
from app.contexts.people.application.use_cases.identifier_use_case import (
    CreateIdentifierUseCase, ListIdentifiersUseCase, GetIdentifierUseCase, UpdateIdentifierUseCase, DeleteIdentifierUseCase,
)
from app.contexts.people.application.use_cases.emergency_use_case import (
    CreateEmergencyContactUseCase, ListEmergencyContactsUseCase, GetEmergencyContactUseCase,
    UpdateEmergencyContactUseCase, DeleteEmergencyContactUseCase,
)
from app.shared.schemas.responses import ApiResponseSingle, ApiResponsePaginated, PaginationResponse

people_router     = APIRouter(prefix="/people", tags=["People"])
address_router    = APIRouter(prefix="/people", tags=["Address"])
contact_router    = APIRouter(prefix="/people", tags=["Contact"])
identity_router   = APIRouter(prefix="/people", tags=["Identity"])
social_router     = APIRouter(prefix="/people", tags=["Social"])
validation_router = APIRouter(prefix="/people", tags=["Validation"])


# ── PERSON ─────────────────────────────────────────────────────────────────────

@people_router.get("", response_model=ApiResponsePaginated[PersonResponseDTO])
async def list_persons(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    items, total, pages = await ListPersonsUseCase().execute(page=page, limit=limit)
    return ApiResponsePaginated(
        status_code=200, message="Persons retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=total, pages=pages),
    )


@people_router.get("/{uuid_person}", response_model=ApiResponseSingle[PersonResponseDTO])
async def get_person(uuid_person: str):
    result = await GetPersonUseCase().execute(uuid_person=uuid_person)
    return ApiResponseSingle(status_code=200, message="Person found.", data=result)


@people_router.post("", response_model=ApiResponseSingle[PersonResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_person(payload: CreatePersonDTO):
    result = await CreatePersonUseCase().execute(dto=payload)
    return ApiResponseSingle(status_code=201, message="Person created.", data=result)


@people_router.patch("/{uuid_person}/status", response_model=ApiResponseSingle[None])
async def update_person_status(uuid_person: str, payload: UpdatePersonStatusDTO):
    await UpdatePersonStatusUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Status updated.")


@people_router.patch("/{uuid_person}", response_model=ApiResponseSingle[PersonResponseDTO])
async def update_person(uuid_person: str, payload: UpdatePersonDTO):
    result = await UpdatePersonUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Person updated.", data=result)


@people_router.delete("/{uuid_person}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(uuid_person: str):
    await DeletePersonUseCase().execute(uuid_person=uuid_person)


@validation_router.get("/check-exists", response_model=ApiResponseSingle[PersonExistsResponseDTO])
async def check_person_exists(
    email: Optional[str] = Query(None),
    personal_id: Optional[str] = Query(None),
    phone_code: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
):
    if not email and not personal_id and not (phone_code and phone_number):
        raise HTTPException(status_code=400, detail="Provide at least one identifier: email, personal_id, or phone_code+phone_number.")
    result = await CheckPersonExistsUseCase().execute(
        email=email, personal_id=personal_id, phone_code=phone_code, phone_number=phone_number,
    )
    return ApiResponseSingle(status_code=200, message="Check completed.", data=result)


# ── ADDRESS ────────────────────────────────────────────────────────────────────

@address_router.post("/{uuid_person}/addresses", response_model=ApiResponseSingle[None], status_code=status.HTTP_201_CREATED)
async def create_address(uuid_person: str, payload: CreateAddressDTO):
    await CreateAddressUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Address saved.")


@address_router.get("/{uuid_person}/addresses", response_model=ApiResponsePaginated[AddressResponseDTO])
async def list_addresses(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    items = await ListAddressesUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Addresses retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, -(-len(items) // limit))),
    )


@address_router.get("/addresses/{uuid_address}", response_model=ApiResponseSingle[AddressResponseDTO])
async def get_address(uuid_address: str):
    result = await GetAddressUseCase().execute(uuid_address=uuid_address)
    return ApiResponseSingle(status_code=200, message="Address found.", data=result)


@address_router.patch("/addresses/{uuid_address}", response_model=ApiResponseSingle[AddressResponseDTO])
async def update_address(uuid_address: str, payload: UpdateAddressDTO):
    result = await UpdateAddressUseCase().execute(uuid_address=uuid_address, dto=payload)
    return ApiResponseSingle(status_code=200, message="Address updated.", data=result)


@address_router.delete("/addresses/{uuid_address}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(uuid_address: str):
    await DeleteAddressUseCase().execute(uuid_address=uuid_address)


# ── EMAILS ─────────────────────────────────────────────────────────────────────

@contact_router.post("/{uuid_person}/emails", response_model=ApiResponseSingle[EmailResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_email(uuid_person: str, payload: CreateEmailDTO):
    result = await CreateEmailUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Email added.", data=result)


@contact_router.get("/{uuid_person}/emails", response_model=ApiResponsePaginated[EmailResponseDTO])
async def list_emails(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    items = await ListEmailsUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Emails retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, -(-len(items) // limit))),
    )


@contact_router.get("/emails/{uuid_email}", response_model=ApiResponseSingle[EmailResponseDTO])
async def get_email(uuid_email: str):
    result = await GetEmailUseCase().execute(uuid_email=uuid_email)
    return ApiResponseSingle(status_code=200, message="Email found.", data=result)


@contact_router.patch("/emails/{uuid_email}", response_model=ApiResponseSingle[EmailResponseDTO])
async def update_email(uuid_email: str, payload: UpdateEmailDTO):
    result = await UpdateEmailUseCase().execute(uuid_email=uuid_email, dto=payload)
    return ApiResponseSingle(status_code=200, message="Email updated.", data=result)


@contact_router.delete("/emails/{uuid_email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(uuid_email: str):
    await DeleteEmailUseCase().execute(uuid_email=uuid_email)


# ── PHONES ─────────────────────────────────────────────────────────────────────

@contact_router.post("/{uuid_person}/phones", response_model=ApiResponseSingle[PhoneResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_phone(uuid_person: str, payload: CreatePhoneDTO):
    result = await CreatePhoneUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Phone added.", data=result)


@contact_router.get("/{uuid_person}/phones", response_model=ApiResponsePaginated[PhoneResponseDTO])
async def list_phones(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    items = await ListPhonesUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Phones retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, -(-len(items) // limit))),
    )


@contact_router.get("/phones/{uuid_phone}", response_model=ApiResponseSingle[PhoneResponseDTO])
async def get_phone(uuid_phone: str):
    result = await GetPhoneUseCase().execute(uuid_phone=uuid_phone)
    return ApiResponseSingle(status_code=200, message="Phone found.", data=result)


@contact_router.patch("/phones/{uuid_phone}", response_model=ApiResponseSingle[PhoneResponseDTO])
async def update_phone(uuid_phone: str, payload: UpdatePhoneDTO):
    result = await UpdatePhoneUseCase().execute(uuid_phone=uuid_phone, dto=payload)
    return ApiResponseSingle(status_code=200, message="Phone updated.", data=result)


@contact_router.delete("/phones/{uuid_phone}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phone(uuid_phone: str):
    await DeletePhoneUseCase().execute(uuid_phone=uuid_phone)


# ── IDENTIFIERS ────────────────────────────────────────────────────────────────

@identity_router.post("/{uuid_person}/identifiers", response_model=ApiResponseSingle[IdentifierResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_identifier(uuid_person: str, payload: CreateIdentifierDTO):
    result = await CreateIdentifierUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Identifier added.", data=result)


@identity_router.get("/{uuid_person}/identifiers", response_model=ApiResponsePaginated[IdentifierResponseDTO])
async def list_identifiers(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    items = await ListIdentifiersUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Identifiers retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, -(-len(items) // limit))),
    )


@identity_router.get("/identifiers/{uuid_identifier}", response_model=ApiResponseSingle[IdentifierResponseDTO])
async def get_identifier(uuid_identifier: str):
    result = await GetIdentifierUseCase().execute(uuid_identifier=uuid_identifier)
    return ApiResponseSingle(status_code=200, message="Identifier found.", data=result)


@identity_router.patch("/identifiers/{uuid_identifier}", response_model=ApiResponseSingle[IdentifierResponseDTO])
async def update_identifier(uuid_identifier: str, payload: UpdateIdentifierDTO):
    result = await UpdateIdentifierUseCase().execute(uuid_identifier=uuid_identifier, dto=payload)
    return ApiResponseSingle(status_code=200, message="Identifier updated.", data=result)


@identity_router.delete("/identifiers/{uuid_identifier}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_identifier(uuid_identifier: str):
    await DeleteIdentifierUseCase().execute(uuid_identifier=uuid_identifier)


# ── EMERGENCY CONTACTS ─────────────────────────────────────────────────────────

@social_router.post("/{uuid_person}/emergency-contacts", response_model=ApiResponseSingle[EmergencyContactResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(uuid_person: str, payload: CreateEmergencyContactDTO):
    result = await CreateEmergencyContactUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Emergency contact added.", data=result)


@social_router.get("/{uuid_person}/emergency-contacts", response_model=ApiResponsePaginated[EmergencyContactResponseDTO])
async def list_emergency_contacts(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    items = await ListEmergencyContactsUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Emergency contacts retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, -(-len(items) // limit))),
    )


@social_router.get("/emergency-contacts/{uuid_emergency}", response_model=ApiResponseSingle[EmergencyContactResponseDTO])
async def get_emergency_contact(uuid_emergency: str):
    result = await GetEmergencyContactUseCase().execute(uuid_emergency=uuid_emergency)
    return ApiResponseSingle(status_code=200, message="Emergency contact found.", data=result)


@social_router.patch("/emergency-contacts/{uuid_emergency}", response_model=ApiResponseSingle[EmergencyContactResponseDTO])
async def update_emergency_contact(uuid_emergency: str, payload: UpdateEmergencyContactDTO):
    result = await UpdateEmergencyContactUseCase().execute(uuid_emergency=uuid_emergency, dto=payload)
    return ApiResponseSingle(status_code=200, message="Emergency contact updated.", data=result)


@social_router.delete("/emergency-contacts/{uuid_emergency}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(uuid_emergency: str):
    await DeleteEmergencyContactUseCase().execute(uuid_emergency=uuid_emergency)
