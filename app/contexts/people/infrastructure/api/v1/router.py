"""
People endpoints for the Digital Hospital ecosystem.

Owns the `people` schema: Person, Email, Phone, Address, PersonalIdentifier,
Birth, LegalInfo, Profile, SocialPlatform, SocialLinks, EmergencyContact.
"""

import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from dh_shared import Person

from app.contexts.people.application.dtos.people_dto import (
    CreatePersonDTO, PersonResponseDTO, CreateAddressDTO, UpdateAddressDTO, AddressResponseDTO,
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
from app.contexts.people.application.use_cases.address_use_case import ListAddressesUseCase, UpdateAddressUseCase, DeleteAddressUseCase
from app.contexts.people.application.use_cases.email_use_case import CreateEmailUseCase, ListEmailsUseCase, UpdateEmailUseCase, DeleteEmailUseCase
from app.contexts.people.application.use_cases.phone_use_case import CreatePhoneUseCase, ListPhonesUseCase, UpdatePhoneUseCase, DeletePhoneUseCase
from app.contexts.people.application.use_cases.identifier_use_case import CreateIdentifierUseCase, ListIdentifiersUseCase, UpdateIdentifierUseCase, DeleteIdentifierUseCase
from app.contexts.people.application.use_cases.emergency_use_case import CreateEmergencyContactUseCase, ListEmergencyContactsUseCase, UpdateEmergencyContactUseCase, DeleteEmergencyContactUseCase
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.schemas.responses import ApiResponseSingle, ApiResponsePaginated, PaginationResponse
from app.shared.utils.logger import logger

people_router = APIRouter(prefix="/people", tags=["People"])
contact_router = APIRouter(prefix="/people", tags=["Contact"])
identity_router = APIRouter(prefix="/people", tags=["Identity"])
social_router = APIRouter(prefix="/people", tags=["Social"])
address_router = APIRouter(prefix="/people", tags=["Address"])
validation_router = APIRouter(prefix="/people", tags=["Validation"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── PERSON ─────────────────────────────────────────────────────────────────────

@people_router.get("", response_model=ApiResponsePaginated[PersonResponseDTO])
async def list_persons(
    page: int = Query(1, ge=1, description="Page number."),
    limit: int = Query(50, ge=1, le=200, description="Items per page."),
):
    items, total, pages = await ListPersonsUseCase().execute(page=page, limit=limit)
    return ApiResponsePaginated(
        status_code=200, message="Persons retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=total, pages=pages),
    )


@people_router.get("/{uuid_person}", response_model=ApiResponseSingle[PersonResponseDTO])
async def get_person(uuid_person: str):
    """Get a person by UUID. Returns 404 if not found."""
    result = await GetPersonUseCase().execute(uuid_person=uuid_person)
    return ApiResponseSingle(status_code=200, message="Person found.", data=result)


@people_router.post("", response_model=ApiResponseSingle[PersonResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_person(payload: CreatePersonDTO):
    """Create a new person with email, phone, and optional CURP."""
    result = await CreatePersonUseCase().execute(dto=payload)
    return ApiResponseSingle(status_code=201, message="Person created.", data=result)


@people_router.patch("/{uuid_person}/status", response_model=ApiResponseSingle[None])
async def update_person_status(uuid_person: str, payload: UpdatePersonStatusDTO):
    """Update a person's verification status."""
    await UpdatePersonStatusUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Status updated.")


@people_router.patch("/{uuid_person}", response_model=ApiResponseSingle[PersonResponseDTO])
async def update_person(uuid_person: str, payload: UpdatePersonDTO):
    """Update a person's mutable fields."""
    result = await UpdatePersonUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Person updated.", data=result)


@people_router.delete("/{uuid_person}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(uuid_person: str):
    """Soft-delete a person by UUID."""
    await DeletePersonUseCase().execute(uuid_person=uuid_person)


@validation_router.get("/check-exists", response_model=ApiResponseSingle[PersonExistsResponseDTO])
async def check_person_exists(
    email: Optional[str] = Query(None, description="Email address to check"),
    personal_id: Optional[str] = Query(None, description="Personal identifier to check (CURP, NSS, fiscal number)"),
    phone_code: Optional[str] = Query(None, description="Phone country code"),
    phone_number: Optional[str] = Query(None, description="Phone number"),
):
    """Check which registration fields are already in use. UUIDs are logged internally — never returned."""
    if not email and not personal_id and not (phone_code and phone_number):
        raise HTTPException(status_code=400, detail="Provide at least one identifier: email, personal_id, or phone_code+phone_number.")
    result = await CheckPersonExistsUseCase().execute(
        email=email, personal_id=personal_id, phone_code=phone_code, phone_number=phone_number,
    )
    return ApiResponseSingle(status_code=200, message="Check completed.", data=result)


# ── ADDRESS ────────────────────────────────────────────────────────────────────

@address_router.post("/{uuid_person}/address", response_model=ApiResponseSingle[None], status_code=status.HTTP_201_CREATED)
async def create_address(uuid_person: str, payload: CreateAddressDTO):
    """Create an address for a person."""
    await CreateAddressUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Address saved.")


@address_router.get("/{uuid_person}/address", response_model=ApiResponsePaginated[AddressResponseDTO])
async def list_addresses(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all addresses for a person."""
    items = await ListAddressesUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Addresses retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


@address_router.patch("/{uuid_person}/address", response_model=ApiResponseSingle[AddressResponseDTO])
async def update_address(uuid_person: str, payload: UpdateAddressDTO):
    """Update a person's address."""
    result = await UpdateAddressUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Address updated.", data=result)


@address_router.delete("/{uuid_person}/address", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(uuid_person: str):
    """Delete a person's address."""
    await DeleteAddressUseCase().execute(uuid_person=uuid_person)


# ── EMAILS ─────────────────────────────────────────────────────────────────────

@contact_router.post("/{uuid_person}/emails", response_model=ApiResponseSingle[EmailResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_email(uuid_person: str, payload: CreateEmailDTO):
    """Add an email to a person."""
    result = await CreateEmailUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Email added.", data=result)


@contact_router.get("/{uuid_person}/emails", response_model=ApiResponsePaginated[EmailResponseDTO])
async def list_emails(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all emails for a person."""
    items = await ListEmailsUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Emails retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


@contact_router.patch("/{uuid_person}/emails", response_model=ApiResponseSingle[EmailResponseDTO])
async def update_email(uuid_person: str, payload: UpdateEmailDTO):
    """Update a person's email (takes the first/single email)."""
    result = await UpdateEmailUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Email updated.", data=result)


@contact_router.delete("/{uuid_person}/emails", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(uuid_person: str):
    """Delete a person's email (takes the first/single email)."""
    await DeleteEmailUseCase().execute(uuid_person=uuid_person)


# ── PHONES ─────────────────────────────────────────────────────────────────────

@contact_router.post("/{uuid_person}/phones", response_model=ApiResponseSingle[PhoneResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_phone(uuid_person: str, payload: CreatePhoneDTO):
    """Add a phone to a person."""
    result = await CreatePhoneUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Phone added.", data=result)


@contact_router.get("/{uuid_person}/phones", response_model=ApiResponsePaginated[PhoneResponseDTO])
async def list_phones(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all phones for a person."""
    items = await ListPhonesUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Phones retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


@contact_router.patch("/{uuid_person}/phones", response_model=ApiResponseSingle[PhoneResponseDTO])
async def update_phone(uuid_person: str, payload: UpdatePhoneDTO):
    """Update a person's phone (takes the first/single phone)."""
    result = await UpdatePhoneUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Phone updated.", data=result)


@contact_router.delete("/{uuid_person}/phones", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phone(uuid_person: str):
    """Delete a person's phone (takes the first/single phone)."""
    await DeletePhoneUseCase().execute(uuid_person=uuid_person)


# ── IDENTIFIERS ────────────────────────────────────────────────────────────────

@identity_router.post("/{uuid_person}/identifiers", response_model=ApiResponseSingle[IdentifierResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_identifier(uuid_person: str, payload: CreateIdentifierDTO):
    """Add a personal identifier (CURP, RFC, etc.) to a person."""
    result = await CreateIdentifierUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Identifier added.", data=result)


@identity_router.get("/{uuid_person}/identifiers", response_model=ApiResponsePaginated[IdentifierResponseDTO])
async def list_identifiers(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all personal identifiers for a person."""
    items = await ListIdentifiersUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Identifiers retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


@identity_router.patch("/{uuid_person}/identifiers", response_model=ApiResponseSingle[IdentifierResponseDTO])
async def update_identifier(uuid_person: str, payload: UpdateIdentifierDTO):
    """Update a person's identifier (takes the first/single identifier)."""
    result = await UpdateIdentifierUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Identifier updated.", data=result)


@identity_router.delete("/{uuid_person}/identifiers", status_code=status.HTTP_204_NO_CONTENT)
async def delete_identifier(uuid_person: str):
    """Delete a person's identifier (takes the first/single identifier)."""
    await DeleteIdentifierUseCase().execute(uuid_person=uuid_person)


# ── EMERGENCY CONTACTS ─────────────────────────────────────────────────────────

@social_router.post("/{uuid_person}/emergency-contacts", response_model=ApiResponseSingle[EmergencyContactResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(uuid_person: str, payload: CreateEmergencyContactDTO):
    """Add an emergency contact for a person."""
    result = await CreateEmergencyContactUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Emergency contact added.", data=result)


@social_router.get("/{uuid_person}/emergency-contacts", response_model=ApiResponsePaginated[EmergencyContactResponseDTO])
async def list_emergency_contacts(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all emergency contacts for a person."""
    items = await ListEmergencyContactsUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Emergency contacts retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


@social_router.patch("/{uuid_person}/emergency-contacts", response_model=ApiResponseSingle[EmergencyContactResponseDTO])
async def update_emergency_contact(uuid_person: str, payload: UpdateEmergencyContactDTO):
    """Update a person's emergency contact (takes the first/single contact)."""
    result = await UpdateEmergencyContactUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Emergency contact updated.", data=result)


@social_router.delete("/{uuid_person}/emergency-contacts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(uuid_person: str):
    """Delete a person's emergency contact (takes the first/single contact)."""
    await DeleteEmergencyContactUseCase().execute(uuid_person=uuid_person)
