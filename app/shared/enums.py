from enum import Enum


class EVerificationStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EGenderIdentity(str, Enum):
    NO_ESPECIFICADO = "NO_ESPECIFICADO"
    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"
    TRANSGENERO = "TRANSGENERO"
    TRANSEXUAL = "TRANSEXUAL"
    TRAVESTI = "TRAVESTI"
    INTERSEXUAL = "INTERSEXUAL"
    OTRO = "OTRO"


class EEmailType(str, Enum):
    PERSONAL = "PERSONAL"
    WORK = "WORK"
    BUSINESS = "BUSINESS"
    OTHER = "OTHER"


class EPhoneType(str, Enum):
    MOBILE = "MOBILE"
    WORK = "WORK"
    HOME = "HOME"
    BUSINESS = "BUSINESS"
    OTHER = "OTHER"


class EAddressType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"
    BUSINESS = "BUSINESS"
    OTHER = "OTHER"


class EIdentifierType(str, Enum):
    NATIONAL_ID = "NATIONAL_ID"
    FISCAL_ID = "FISCAL_ID"
    SOCIAL_SECURITY_ID = "SOCIAL_SECURITY_ID"


class ENationalIdSex(str, Enum):
    H = "H"
    M = "M"
    X = "X"


class ECivilStatus(str, Enum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    COMMON_LAW = "COMMON_LAW"
    SEPARATED = "SEPARATED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"
    PREFERS_NOT_TO_SAY = "PREFERS_NOT_TO_SAY"
