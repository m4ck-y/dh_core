from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from dh_shared.enums import (
    EAddressType, EVerificationStatus, EEmailType, EPhoneType, EIdentifierType, ERelationshipContact,
)


class PersonalIdentifierInputDTO(BaseModel):
    """Sub-object for personal identifier input. type defaults to NATIONAL_ID (CURP)."""
    type: EIdentifierType = Field(default=EIdentifierType.NATIONAL_ID, description="Identifier type.", examples=["NATIONAL_ID"])
    value: str = Field(..., description="Identifier value (CURP, NSS, fiscal number).", examples=["PEGJ900515HJCRRC09"])


class CreatePersonDTO(BaseModel):
    email: EmailStr = Field(..., description="Email of the person.", examples=["user@example.com"])
    phone_code: str = Field(..., description="Country code.", examples=["+52"])
    phone_number: str = Field(..., description="Phone number.", examples=["5512345678"])
    first_name: str = Field(..., description="Given name(s).", examples=["Juan"])
    last_name: str = Field(..., description="First last name.", examples=["Perez"])
    second_last_name: Optional[str] = Field(None, description="Second last name.", examples=["Garcia"])
    birth_date: date = Field(..., description="Date of birth.", examples=["1990-05-15"])
    key_birth_country: str = Field(..., description="Country code of birth.", examples=["MX"])
    key_birth_state: Optional[str] = Field(None, description="State code of birth.", examples=["CMX"])
    type_gender: Optional[str] = Field(None, description="Gender identity.", examples=["MASCULINO"])
    key_nationality: Optional[str] = Field(None, description="Nationality code.", examples=["MX"])
    personal_identifier: Optional[PersonalIdentifierInputDTO] = Field(None, description="Optional personal identifier (CURP, NSS, fiscal number).")

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.strip().lower()


class PersonResponseDTO(BaseModel):
    uuid: UUID = Field(..., description="Person UUID.", examples=["550e8400-e29b-41d4-a716-446655440000"])
    first_name: Optional[str] = Field(None, description="Given name(s).", examples=["Juan"])
    last_name: Optional[str] = Field(None, description="First last name.", examples=["Perez"])
    second_last_name: Optional[str] = Field(None, description="Second last name.")
    type_gender: Optional[str] = Field(None, description="Gender identity.")
    verification_status: EVerificationStatus = Field(..., description="Identity verification status.")


class CreateAddressDTO(BaseModel):
    postal_code: str = Field(..., description="Postal code.", examples=["06600"])
    key_state: str = Field(..., description="State code.", examples=["CMX"])
    key_municipality: str = Field(..., description="Municipality code.", examples=["016"])
    key_colony: Optional[str] = Field(None, description="Colony/neighborhood code.")
    address: str = Field(..., description="Street address.", examples=["Av. Reforma 123"])
    address_complement: Optional[str] = Field(None, description="Address complement.", examples=["Depto 4B"])
    type_address: EAddressType = Field(EAddressType.HOME, description="Address type.")


class UpdatePersonStatusDTO(BaseModel):
    verification_status: EVerificationStatus = Field(..., description="New verification status.")


class UpdatePersonDTO(BaseModel):
    first_name: Optional[str] = Field(None, description="Updated first name.", examples=["Juan"])
    last_name: Optional[str] = Field(None, description="Updated last name.", examples=["Perez"])
    second_last_name: Optional[str] = Field(None, description="Updated second last name.")
    type_gender: Optional[str] = Field(None, description="Updated gender identity.")
    verification_status: Optional[EVerificationStatus] = Field(None, description="Updated verification status.")


class PersonExistsResponseDTO(BaseModel):
    email_already_registered: bool = Field(False, description="Whether the email is already registered by any person.")
    personal_id_already_registered: bool = Field(False, description="Whether the personal identifier (CURP/NSS/fiscal) is already associated with a person.")
    phone_already_registered: bool = Field(False, description="Whether the phone is already registered by any person.")


class CreateEmailDTO(BaseModel):
    email: EmailStr = Field(..., description="Email address.", examples=["user@example.com"])
    type_email: EEmailType = Field(EEmailType.PERSONAL, description="Email type.")


class EmailResponseDTO(BaseModel):
    uuid: UUID = Field(..., description="Email UUID.")
    email: str = Field(..., description="Email address.")
    type_email: EEmailType = Field(..., description="Email type.")


class CreatePhoneDTO(BaseModel):
    code: str = Field(..., description="Country code.", examples=["+52"])
    number: str = Field(..., description="Phone number.", examples=["5512345678"])
    type_phone: EPhoneType = Field(EPhoneType.MOBILE, description="Phone type.")


class PhoneResponseDTO(BaseModel):
    uuid: UUID = Field(..., description="Phone UUID.")
    code: str = Field(..., description="Country code.")
    number: str = Field(..., description="Phone number.")
    type_phone: EPhoneType = Field(..., description="Phone type.")


class CreateIdentifierDTO(BaseModel):
    id_identifier_type: EIdentifierType = Field(..., description="Identifier type.")
    identifier_value: str = Field(..., description="Identifier value.", examples=["PEGJ900515HJCRRC09"])


class IdentifierResponseDTO(BaseModel):
    uuid: UUID = Field(..., description="Identifier UUID.")
    type: EIdentifierType = Field(..., description="Identifier type.")
    value: str = Field(..., description="Identifier value.")


class CreateEmergencyContactDTO(BaseModel):
    first_name: str = Field(..., description="Contact first name.", examples=["Maria"])
    last_name: str = Field(..., description="Contact last name.", examples=["Lopez"])
    phone_number: Optional[str] = Field(None, description="Contact phone.", examples=["5511111111"])
    email: Optional[str] = Field(None, description="Contact email.")
    relationship_type: ERelationshipContact = Field(..., description="Relationship type.")
    notes: Optional[str] = Field(None, description="Optional notes.")


class UpdateAddressDTO(BaseModel):
    postal_code: Optional[str] = Field(None)
    key_state: Optional[str] = Field(None)
    key_municipality: Optional[str] = Field(None)
    key_colony: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    address_complement: Optional[str] = Field(None)
    type_address: Optional[EAddressType] = Field(None)


class AddressResponseDTO(BaseModel):
    uuid: UUID = Field(..., description="Address UUID.")
    type_address: EAddressType
    postal_code: Optional[str] = Field(None)
    key_state: Optional[str] = Field(None)
    key_municipality: Optional[str] = Field(None)
    key_colony: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    address_complement: Optional[str] = Field(None)


class UpdateEmailDTO(BaseModel):
    type_email: Optional[EEmailType] = Field(None, description="Updated email type.")


class UpdatePhoneDTO(BaseModel):
    code: Optional[str] = Field(None, description="Updated country code.", examples=["+52"])
    number: Optional[str] = Field(None, description="Updated phone number.", examples=["5512345678"])
    type_phone: Optional[EPhoneType] = Field(None, description="Updated phone type.")


class UpdateIdentifierDTO(BaseModel):
    id_identifier_type: Optional[EIdentifierType] = Field(None)
    identifier_value: Optional[str] = Field(None, examples=["PEGJ900515HJCRRC09"])


class UpdateEmergencyContactDTO(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    phone_number: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    relationship_type: Optional[ERelationshipContact] = Field(None)
    notes: Optional[str] = Field(None)


class EmergencyContactResponseDTO(BaseModel):
    uuid: UUID = Field(..., description="Contact UUID.")
    first_name: Optional[str] = Field(None, description="Contact first name.")
    last_name: Optional[str] = Field(None, description="Contact last name.")
    phone_number: Optional[str] = Field(None, description="Contact phone.")
    email: Optional[str] = Field(None)
    relationship_type: ERelationshipContact = Field(..., description="Relationship type.")
    notes: Optional[str] = Field(None)
