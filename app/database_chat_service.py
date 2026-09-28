from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Company, Job, Office


settings = get_settings()

openai_client = OpenAI(
    api_key=settings.openai_api_key or "missing-key"
)


DATABASE_SYSTEM_PROMPT = """
You are Knowva AI, the official company and careers assistant.

Answer using only the supplied PostgreSQL company data.

The database is the current source of truth for:
- Company information
- Office locations
- Current job openings
- Job locations
- Work models
- Experience requirements
- Salaries
- Skills and qualifications
- Application links

Rules:
1. Never invent companies, offices, jobs, salaries, or requirements.
2. Only show jobs whose status is open.
3. When asked for all matching jobs, examine every supplied job.
4. Apply location, experience, work-model, salary, title, department, and
   skill requirements carefully.
5. A candidate matches an experience range when their experience is greater
   than or equal to the minimum and less than or equal to the maximum.
6. Remote jobs can match a request that allows remote work.
7. Include the job title, job code, location, work model, experience range,
   salary range, and application URL when available.
8. Format multiple jobs as a clear bullet list.
9. Do not mention database implementation details.
10. If the question cannot be answered from the company, office, or job data,
    respond with exactly: DATABASE_NOT_RELEVANT
"""


def format_company(
    company: Company,
) -> str:
    return f"""
COMPANY
Name: {company.name}
Legal name: {company.legal_name}
Description: {company.description}
Industry: {company.industry}
Founded: {company.founded_year}
Employee count: {company.employee_count}
Website: {company.website}
Email: {company.email}
Phone: {company.phone}
Headquarters: {company.city}, {company.state}, {company.country}
Mission: {company.mission}
Values: {company.company_values}
Products and services: {company.products_services}
""".strip()


def format_office(
    office: Office,
) -> str:
    return f"""
OFFICE
Name: {office.office_name}
Address: {office.address_line_1}
Address line 2: {office.address_line_2}
City: {office.city}
State: {office.state}
Country: {office.country}
Postal code: {office.postal_code}
Phone: {office.phone}
Email: {office.email}
Headquarters: {office.is_headquarters}
""".strip()


def format_job(
    job: Job,
) -> str:
    if job.city:
        location = ", ".join(
            part
            for part in [
                job.city,
                job.state,
                job.country,
            ]
            if part
        )
    else:
        location = job.country or "Not specified"

    return f"""
JOB
Job code: {job.job_code}
Title: {job.title}
Department: {job.department}
Description: {job.description}
Responsibilities: {job.responsibilities}
Required qualifications: {job.required_qualifications}
Preferred qualifications: {job.preferred_qualifications}
Skills: {job.skills}
Employment type: {job.employment_type}
Work model: {job.work_model}
Location: {location}
Minimum experience: {job.minimum_experience}
Maximum experience: {job.maximum_experience}
Minimum salary: {job.minimum_salary}
Maximum salary: {job.maximum_salary}
Application URL: {job.application_url}
Posted at: {job.posted_at}
Closing at: {job.closing_at}
Status: {job.status}
""".strip()


def build_database_context(
    database: Session,
) -> str | None:
    companies = list(
        database.scalars(
            select(Company).order_by(Company.name)
        ).all()
    )

    offices = list(
        database.scalars(
            select(Office).order_by(
                Office.is_headquarters.desc(),
                Office.city,
            )
        ).all()
    )

    jobs = list(
        database.scalars(
            select(Job)
            .where(Job.status.ilike("open"))
            .order_by(Job.title)
        ).all()
    )

    if not companies and not offices and not jobs:
        return None

    context_parts: list[str] = []

    for company in companies:
        context_parts.append(
            format_company(company)
        )

    for office in offices:
        context_parts.append(
            format_office(office)
        )

    for job in jobs:
        context_parts.append(
            format_job(job)
        )

    return "\n\n---\n\n".join(
        context_parts
    )


def answer_database_question(
    database: Session,
    question: str,
) -> str | None:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured"
        )

    database_context = build_database_context(
        database
    )

    if database_context is None:
        return None

    user_prompt = f"""
Current company database:

{database_context}

User question:
{question}

Answer from the database if it contains the requested information.
Otherwise respond with exactly DATABASE_NOT_RELEVANT.
"""

    completion = openai_client.chat.completions.create(
        model=settings.openai_chat_model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": DATABASE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    answer = (
        completion.choices[0].message.content
        or ""
    ).strip()

    if answer == "DATABASE_NOT_RELEVANT":
        return None

    return answer or None