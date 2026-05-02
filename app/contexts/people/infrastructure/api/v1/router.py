"""
People endpoints for the Digital Hospital ecosystem.

Owns the `people` schema: Person, Email, Phone, Address, PersonalIdentifier,
Birth, LegalInfo, Profile, SocialPlatform, SocialLinks, EmergencyContact.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from dh_shared import Person

from app.contexts.people.application.dtos.people_dto import (
    CreatePersonDTO, PersonResponseDTO, CreateAddressDTO, UpdatePersonStatusDTO, PersonExistsResponseDTO,
    CreateEmailDTO, EmailResponseDTO, CreatePhoneDTO, PhoneResponseDTO,
    CreateIdentifierDTO, IdentifierResponseDTO,
    CreateEmergencyContactDTO, EmergencyContactResponseDTO,
)
from app.contexts.people.application.use_cases.create_person_use_case import CreatePersonUseCase
from app.contexts.people.application.use_cases.get_person_use_case import GetPersonUseCase
from app.contexts.people.application.use_cases.create_address_use_case import CreateAddressUseCase
from app.contexts.people.application.use_cases.update_person_status_use_case import UpdatePersonStatusUseCase
from app.contexts.people.application.use_cases.check_person_exists_use_case import CheckPersonExistsUseCase
from app.contexts.people.application.use_cases.email_use_case import CreateEmailUseCase, ListEmailsUseCase
from app.contexts.people.application.use_cases.phone_use_case import CreatePhoneUseCase, ListPhonesUseCase
from app.contexts.people.application.use_cases.identifier_use_case import CreateIdentifierUseCase, ListIdentifiersUseCase
from app.contexts.people.application.use_cases.emergency_use_case import CreateEmergencyContactUseCase, ListEmergencyContactsUseCase
from app.shared.database.postgres import AsyncSessionLocal
from app.shared.schemas.responses import ApiResponseSingle, ApiResponsePaginated, PaginationResponse
from app.shared.utils.logger import logger

people_router = APIRouter(prefix="/people", tags=["People"])
contact_router = APIRouter(prefix="/people", tags=["Contact"])
identity_router = APIRouter(prefix="/people", tags=["Identity"])
social_router = APIRouter(prefix="/people", tags=["Social"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── PERSON ─────────────────────────────────────────────────────────────────────

@people_router.get("/persons/{uuid_person}", response_model=ApiResponseSingle[PersonResponseDTO])
async def get_person(uuid_person: str):
    """Get a person by UUID. Returns 404 if not found."""
    result = await GetPersonUseCase().execute(uuid_person=uuid_person)
    return ApiResponseSingle(status_code=200, message="Person found.", data=result)


@people_router.post("/persons", response_model=ApiResponseSingle[PersonResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_person(payload: CreatePersonDTO):
    """Create a new person with email, phone, and optional CURP."""
    result = await CreatePersonUseCase().execute(dto=payload)
    return ApiResponseSingle(status_code=201, message="Person created.", data=result)


@people_router.patch("/persons/{uuid_person}/status", response_model=ApiResponseSingle[None])
async def update_person_status(uuid_person: str, payload: UpdatePersonStatusDTO):
    """Update a person's verification status."""
    await UpdatePersonStatusUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=200, message="Status updated.")


@people_router.get("/persons/check-exists", response_model=ApiResponseSingle[PersonExistsResponseDTO])
async def check_person_exists(
    email: Optional[str] = Query(None, description="Email address to check"),
    curp: Optional[str] = Query(None, description="CURP to check"),
):
    """Check if a person exists by email or CURP."""
    if not email and not curp:
        raise HTTPException(status_code=400, detail="Provide email or curp.")
    uc = CheckPersonExistsUseCase()
    if email and curp:
        result = await uc.by_email_or_curp(email=email, curp=curp)
    elif email:
        result = await uc.by_email(email=email)
    else:
        result = await uc.by_curp(curp=curp)
    return ApiResponseSingle(status_code=200, message="Check completed.", data=result)


# ── ADDRESS ────────────────────────────────────────────────────────────────────

@people_router.post("/persons/{uuid_person}/address", response_model=ApiResponseSingle[None], status_code=status.HTTP_201_CREATED)
async def create_address(uuid_person: str, payload: CreateAddressDTO):
    """Create an address for a person."""
    await CreateAddressUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Address saved.")


# ── EMAILS ─────────────────────────────────────────────────────────────────────

@contact_router.post("/persons/{uuid_person}/emails", response_model=ApiResponseSingle[EmailResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_email(uuid_person: str, payload: CreateEmailDTO):
    """Add an email to a person."""
    result = await CreateEmailUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Email added.", data=result)


@contact_router.get("/persons/{uuid_person}/emails", response_model=ApiResponsePaginated[EmailResponseDTO])
async def list_emails(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all emails for a person."""
    items = await ListEmailsUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Emails retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


# ── PHONES ─────────────────────────────────────────────────────────────────────

@contact_router.post("/persons/{uuid_person}/phones", response_model=ApiResponseSingle[PhoneResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_phone(uuid_person: str, payload: CreatePhoneDTO):
    """Add a phone to a person."""
    result = await CreatePhoneUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Phone added.", data=result)


@contact_router.get("/persons/{uuid_person}/phones", response_model=ApiResponsePaginated[PhoneResponseDTO])
async def list_phones(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all phones for a person."""
    items = await ListPhonesUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Phones retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


# ── IDENTIFIERS ────────────────────────────────────────────────────────────────

@identity_router.post("/persons/{uuid_person}/identifiers", response_model=ApiResponseSingle[IdentifierResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_identifier(uuid_person: str, payload: CreateIdentifierDTO):
    """Add a personal identifier (CURP, RFC, etc.) to a person."""
    result = await CreateIdentifierUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Identifier added.", data=result)


@identity_router.get("/persons/{uuid_person}/identifiers", response_model=ApiResponsePaginated[IdentifierResponseDTO])
async def list_identifiers(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all personal identifiers for a person."""
    items = await ListIdentifiersUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Identifiers retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )


# ── EMERGENCY CONTACTS ─────────────────────────────────────────────────────────

@social_router.post("/persons/{uuid_person}/emergency-contacts", response_model=ApiResponseSingle[EmergencyContactResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(uuid_person: str, payload: CreateEmergencyContactDTO):
    """Add an emergency contact for a person."""
    result = await CreateEmergencyContactUseCase().execute(uuid_person=uuid_person, dto=payload)
    return ApiResponseSingle(status_code=201, message="Emergency contact added.", data=result)


@social_router.get("/persons/{uuid_person}/emergency-contacts", response_model=ApiResponsePaginated[EmergencyContactResponseDTO])
async def list_emergency_contacts(uuid_person: str, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """List all emergency contacts for a person."""
    items = await ListEmergencyContactsUseCase().execute(uuid_person=uuid_person)
    return ApiResponsePaginated(
        status_code=200, message="Emergency contacts retrieved.", data=items,
        pagination=PaginationResponse(page=page, limit=limit, total=len(items), pages=max(1, len(items) // limit + 1)),
    )
