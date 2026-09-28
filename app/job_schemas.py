from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class JobBase(BaseModel):
    company_id: UUID
    office_id: UUID | None = None

    job_code: str = Field(
        min_length=1,
        max_length=100,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    description: str = Field(
        min_length=1,
    )

    responsibilities: str | None = None
    required_qualifications: str | None = None
    preferred_qualifications: str | None = None
    skills: str | None = None

    employment_type: str | None = Field(
        default=None,
        max_length=100,
    )

    work_model: str | None = Field(
        default=None,
        max_length=50,
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

    minimum_experience: int | None = Field(
        default=None,
        ge=0,
    )

    maximum_experience: int | None = Field(
        default=None,
        ge=0,
    )

    minimum_salary: int | None = Field(
        default=None,
        ge=0,
    )

    maximum_salary: int | None = Field(
        default=None,
        ge=0,
    )

    application_url: str | None = Field(
        default=None,
        max_length=1000,
    )

    posted_at: datetime | None = None
    closing_at: datetime | None = None

    status: str = Field(
        default="open",
        max_length=50,
    )

    @model_validator(mode="after")
    def validate_ranges(self):
        if (
            self.minimum_experience is not None
            and self.maximum_experience is not None
            and self.maximum_experience < self.minimum_experience
        ):
            raise ValueError(
                "maximum_experience must be greater than or equal "
                "to minimum_experience"
            )

        if (
            self.minimum_salary is not None
            and self.maximum_salary is not None
            and self.maximum_salary < self.minimum_salary
        ):
            raise ValueError(
                "maximum_salary must be greater than or equal "
                "to minimum_salary"
            )

        if (
            self.posted_at is not None
            and self.closing_at is not None
            and self.closing_at < self.posted_at
        ):
            raise ValueError(
                "closing_at must be after posted_at"
            )

        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    office_id: UUID | None = None

    job_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    responsibilities: str | None = None
    required_qualifications: str | None = None
    preferred_qualifications: str | None = None
    skills: str | None = None

    employment_type: str | None = Field(
        default=None,
        max_length=100,
    )

    work_model: str | None = Field(
        default=None,
        max_length=50,
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

    minimum_experience: int | None = Field(
        default=None,
        ge=0,
    )

    maximum_experience: int | None = Field(
        default=None,
        ge=0,
    )

    minimum_salary: int | None = Field(
        default=None,
        ge=0,
    )

    maximum_salary: int | None = Field(
        default=None,
        ge=0,
    )

    application_url: str | None = Field(
        default=None,
        max_length=1000,
    )

    posted_at: datetime | None = None
    closing_at: datetime | None = None

    status: str | None = Field(
        default=None,
        max_length=50,
    )


class JobResponse(JobBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    created_at: datetime
    updated_at: datetime