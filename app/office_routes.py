from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import get_database_session
from app.models import Company, Office
from app.office_schemas import (
    OfficeCreate,
    OfficeResponse,
    OfficeUpdate,
)


router = APIRouter(
    prefix="/api/offices",
    tags=["Offices"],
)


def clear_existing_headquarters(
    database: Session,
    company_id: UUID,
    excluded_office_id: UUID | None = None,
) -> None:
    statement = (
        update(Office)
        .where(Office.company_id == company_id)
        .values(is_headquarters=False)
    )

    if excluded_office_id is not None:
        statement = statement.where(
            Office.id != excluded_office_id
        )

    database.execute(statement)


@router.post(
    "",
    response_model=OfficeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_office(
    office_data: OfficeCreate,
    database: Session = Depends(get_database_session),
) -> Office:
    company = database.get(
        Company,
        office_data.company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    if office_data.is_headquarters:
        clear_existing_headquarters(
            database,
            office_data.company_id,
        )

    office = Office(
        **office_data.model_dump()
    )

    database.add(office)
    database.commit()
    database.refresh(office)

    return office


@router.get(
    "",
    response_model=list[OfficeResponse],
)
def list_offices(
    company_id: UUID | None = Query(
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
    is_headquarters: bool | None = Query(
        default=None
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
) -> list[Office]:
    statement = select(Office)

    if company_id is not None:
        statement = statement.where(
            Office.company_id == company_id
        )

    if city:
        statement = statement.where(
            Office.city.ilike(f"%{city}%")
        )

    if state_name:
        statement = statement.where(
            Office.state.ilike(f"%{state_name}%")
        )

    if country:
        statement = statement.where(
            Office.country.ilike(f"%{country}%")
        )

    if is_headquarters is not None:
        statement = statement.where(
            Office.is_headquarters == is_headquarters
        )

    statement = (
        statement
        .order_by(
            Office.is_headquarters.desc(),
            Office.city,
            Office.office_name,
        )
        .offset(skip)
        .limit(limit)
    )

    offices = database.scalars(
        statement
    ).all()

    return list(offices)


@router.get(
    "/{office_id}",
    response_model=OfficeResponse,
)
def get_office(
    office_id: UUID,
    database: Session = Depends(get_database_session),
) -> Office:
    office = database.get(
        Office,
        office_id,
    )

    if office is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found",
        )

    return office


@router.put(
    "/{office_id}",
    response_model=OfficeResponse,
)
def update_office(
    office_id: UUID,
    office_data: OfficeUpdate,
    database: Session = Depends(get_database_session),
) -> Office:
    office = database.get(
        Office,
        office_id,
    )

    if office is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found",
        )

    update_data = office_data.model_dump(
        exclude_unset=True
    )

    required_fields = {
        "office_name",
        "address_line_1",
        "city",
        "state",
        "country",
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

    if update_data.get("is_headquarters") is True:
        clear_existing_headquarters(
            database,
            office.company_id,
            excluded_office_id=office.id,
        )

    for field_name, value in update_data.items():
        setattr(
            office,
            field_name,
            value,
        )

    database.commit()
    database.refresh(office)

    return office


@router.delete(
    "/{office_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_office(
    office_id: UUID,
    database: Session = Depends(get_database_session),
) -> Response:
    office = database.get(
        Office,
        office_id,
    )

    if office is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found",
        )

    database.delete(office)
    database.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )