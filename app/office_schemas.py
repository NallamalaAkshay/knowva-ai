from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OfficeBase(BaseModel):
    company_id: UUID

    office_name: str = Field(
        min_length=1,
        max_length=255,
    )

    address_line_1: str = Field(
        min_length=1,
        max_length=255,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str = Field(
        min_length=1,
        max_length=100,
    )

    state: str = Field(
        min_length=1,
        max_length=100,
    )

    country: str = Field(
        min_length=1,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=30,
    )

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    is_headquarters: bool = False

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


class OfficeCreate(OfficeBase):
    pass


class OfficeUpdate(BaseModel):
    office_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    address_line_1: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=30,
    )

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    is_headquarters: bool | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


class OfficeResponse(OfficeBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    created_at: datetime
    updated_at: datetime