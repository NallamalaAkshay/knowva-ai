from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    industry: str | None = Field(
        default=None,
        max_length=150,
    )

    founded_year: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )

    employee_count: int | None = Field(
        default=None,
        ge=0,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    linkedin_url: str | None = Field(
        default=None,
        max_length=500,
    )

    logo_url: str | None = Field(
        default=None,
        max_length=500,
    )

    address_line_1: str | None = Field(
        default=None,
        max_length=255,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=30,
    )

    mission: str | None = None
    company_values: str | None = None
    products_services: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    industry: str | None = Field(
        default=None,
        max_length=150,
    )

    founded_year: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )

    employee_count: int | None = Field(
        default=None,
        ge=0,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    linkedin_url: str | None = Field(
        default=None,
        max_length=500,
    )

    logo_url: str | None = Field(
        default=None,
        max_length=500,
    )

    address_line_1: str | None = Field(
        default=None,
        max_length=255,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=30,
    )

    mission: str | None = None
    company_values: str | None = None
    products_services: str | None = None


class CompanyResponse(CompanyBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    created_at: datetime
    updated_at: datetime