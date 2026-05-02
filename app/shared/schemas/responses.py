from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class PaginationResponse(BaseModel):
    page: int = Field(..., examples=[1])
    limit: int = Field(..., examples=[100])
    total: int = Field(..., examples=[450])
    pages: int = Field(..., examples=[5])


class ApiResponseBase(BaseModel):
    status_code: int = Field(..., examples=[200])
    internal_code: Optional[int] = Field(None, examples=[0])
    message: Optional[str] = Field(None, examples=["Operation successful."])


class ApiResponseSingle(ApiResponseBase, Generic[T]):
    data: Optional[T] = Field(None)


class ApiResponsePaginated(ApiResponseBase, Generic[T]):
    data: List[T] = Field(...)
    pagination: PaginationResponse = Field(...)
