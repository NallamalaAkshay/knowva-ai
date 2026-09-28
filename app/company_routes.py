from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.company_schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)
from app.database import get_database_session
from app.models import Company


router = APIRouter(
    prefix="/api/companies",
    tags=["Companies"],
)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company_data: CompanyCreate,
    database: Session = Depends(get_database_session),
) -> Company:
    company = Company(
        **company_data.model_dump()
    )

    database.add(company)
    database.commit()
    database.refresh(company)

    return company


@router.get(
    "",
    response_model=list[CompanyResponse],
)
def list_companies(
    name: str | None = Query(
        default=None,
        description="Filter companies by name",
    ),
    industry: str | None = Query(
        default=None,
        description="Filter companies by industry",
    ),
    city: str | None = Query(
        default=None,
        description="Filter companies by city",
    ),
    state: str | None = Query(
        default=None,
        description="Filter companies by state",
    ),
    country: str | None = Query(
        default=None,
        description="Filter companies by country",
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
) -> list[Company]:
    statement = select(Company)

    if name:
        statement = statement.where(
            Company.name.ilike(f"%{name}%")
        )

    if industry:
        statement = statement.where(
            Company.industry.ilike(f"%{industry}%")
        )

    if city:
        statement = statement.where(
            Company.city.ilike(f"%{city}%")
        )

    if state:
        statement = statement.where(
            Company.state.ilike(f"%{state}%")
        )

    if country:
        statement = statement.where(
            Company.country.ilike(f"%{country}%")
        )

    statement = (
        statement
        .order_by(Company.name)
        .offset(skip)
        .limit(limit)
    )

    companies = database.scalars(
        statement
    ).all()

    return list(companies)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: UUID,
    database: Session = Depends(get_database_session),
) -> Company:
    company = database.get(
        Company,
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    database: Session = Depends(get_database_session),
) -> Company:
    company = database.get(
        Company,
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    update_data = company_data.model_dump(
        exclude_unset=True
    )

    if (
        "name" in update_data
        and update_data["name"] is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name cannot be null",
        )

    for field_name, value in update_data.items():
        setattr(
            company,
            field_name,
            value,
        )

    database.commit()
    database.refresh(company)

    return company


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_company(
    company_id: UUID,
    database: Session = Depends(get_database_session),
) -> Response:
    company = database.get(
        Company,
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    database.delete(company)
    database.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )