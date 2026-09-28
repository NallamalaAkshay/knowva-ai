from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_database_session
from app.job_schemas import (
    JobCreate,
    JobResponse,
    JobUpdate,
)
from app.models import Company, Job, Office


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)


def validate_office(
    database: Session,
    company_id: UUID,
    office_id: UUID | None,
) -> None:
    if office_id is None:
        return

    office = database.get(
        Office,
        office_id,
    )

    if office is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found",
        )

    if office.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Office does not belong to this company",
        )


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    database: Session = Depends(get_database_session),
) -> Job:
    company = database.get(
        Company,
        job_data.company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    validate_office(
        database,
        job_data.company_id,
        job_data.office_id,
    )

    job = Job(
        **job_data.model_dump()
    )

    database.add(job)

    try:
        database.commit()
    except IntegrityError as exc:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job with this job code already exists",
        ) from exc

    database.refresh(job)

    return job


@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs(
    company_id: UUID | None = Query(
        default=None
    ),
    office_id: UUID | None = Query(
        default=None
    ),
    search: str | None = Query(
        default=None,
        description=(
            "Search job title, description, department, or skills"
        ),
    ),
    title: str | None = Query(
        default=None
    ),
    department: str | None = Query(
        default=None
    ),
    city: str | None = Query(
        default=None
    ),
    state_name: str | None = Query(
        default=None,
        alias="state",
    ),
    country: str | None = Query(
        default=None
    ),
    work_model: str | None = Query(
        default=None,
        description="Examples: onsite, hybrid, remote",
    ),
    employment_type: str | None = Query(
        default=None,
        description="Examples: full-time, part-time, contract",
    ),
    experience_years: int | None = Query(
        default=None,
        ge=0,
        description="Return jobs accepting this amount of experience",
    ),
    minimum_salary: int | None = Query(
        default=None,
        ge=0,
    ),
    job_status: str | None = Query(
        default="open",
        alias="status",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    database: Session = Depends(get_database_session),
) -> list[Job]:
    statement = select(Job)

    if company_id is not None:
        statement = statement.where(
            Job.company_id == company_id
        )

    if office_id is not None:
        statement = statement.where(
            Job.office_id == office_id
        )

    if search:
        search_value = f"%{search}%"

        statement = statement.where(
            or_(
                Job.title.ilike(search_value),
                Job.description.ilike(search_value),
                Job.department.ilike(search_value),
                Job.skills.ilike(search_value),
            )
        )

    if title:
        statement = statement.where(
            Job.title.ilike(f"%{title}%")
        )

    if department:
        statement = statement.where(
            Job.department.ilike(f"%{department}%")
        )

    if city:
        statement = statement.where(
            Job.city.ilike(f"%{city}%")
        )

    if state_name:
        statement = statement.where(
            Job.state.ilike(f"%{state_name}%")
        )

    if country:
        statement = statement.where(
            Job.country.ilike(f"%{country}%")
        )

    if work_model:
        statement = statement.where(
            Job.work_model.ilike(f"%{work_model}%")
        )

    if employment_type:
        statement = statement.where(
            Job.employment_type.ilike(
                f"%{employment_type}%"
            )
        )

    if experience_years is not None:
        statement = statement.where(
            or_(
                Job.minimum_experience.is_(None),
                Job.minimum_experience <= experience_years,
            ),
            or_(
                Job.maximum_experience.is_(None),
                Job.maximum_experience >= experience_years,
            ),
        )

    if minimum_salary is not None:
        statement = statement.where(
            Job.maximum_salary >= minimum_salary
        )

    if job_status:
        statement = statement.where(
            Job.status.ilike(job_status)
        )

    statement = (
        statement
        .order_by(
            Job.posted_at.desc().nullslast(),
            Job.title,
        )
        .offset(skip)
        .limit(limit)
    )

    jobs = database.scalars(
        statement
    ).all()

    return list(jobs)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: UUID,
    database: Session = Depends(get_database_session),
) -> Job:
    job = database.get(
        Job,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    database: Session = Depends(get_database_session),
) -> Job:
    job = database.get(
        Job,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    update_data = job_data.model_dump(
        exclude_unset=True
    )

    required_fields = {
        "job_code",
        "title",
        "description",
        "status",
    }

    for field_name in required_fields:
        if (
            field_name in update_data
            and update_data[field_name] is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} cannot be null",
            )

    if "office_id" in update_data:
        validate_office(
            database,
            job.company_id,
            update_data["office_id"],
        )

    minimum_experience = update_data.get(
        "minimum_experience",
        job.minimum_experience,
    )

    maximum_experience = update_data.get(
        "maximum_experience",
        job.maximum_experience,
    )

    if (
        minimum_experience is not None
        and maximum_experience is not None
        and maximum_experience < minimum_experience
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "maximum_experience must be greater than or "
                "equal to minimum_experience"
            ),
        )

    minimum_salary = update_data.get(
        "minimum_salary",
        job.minimum_salary,
    )

    maximum_salary = update_data.get(
        "maximum_salary",
        job.maximum_salary,
    )

    if (
        minimum_salary is not None
        and maximum_salary is not None
        and maximum_salary < minimum_salary
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "maximum_salary must be greater than or "
                "equal to minimum_salary"
            ),
        )

    for field_name, value in update_data.items():
        setattr(
            job,
            field_name,
            value,
        )

    try:
        database.commit()
    except IntegrityError as exc:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job with this job code already exists",
        ) from exc

    database.refresh(job)

    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job(
    job_id: UUID,
    database: Session = Depends(get_database_session),
) -> Response:
    job = database.get(
        Job,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    database.delete(job)
    database.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )