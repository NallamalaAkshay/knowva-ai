from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Job


COMPANY_ID = UUID(
    "9c5cd3d6-3a13-4aaf-aa87-92629c6fc393"
)

ALBANY_OFFICE_ID = UUID(
    "aeaf49a1-fcab-41e7-b5de-cd3cb56e4aa1"
)

POSTED_AT = datetime(
    2026,
    9,
    22,
    tzinfo=timezone.utc,
)

CLOSING_AT = datetime(
    2026,
    10,
    31,
    23,
    59,
    59,
    tzinfo=timezone.utc,
)


JOBS = [
    {
        "job_code": "KT-DATA-204",
        "title": "Data Analyst",
        "department": "Business Intelligence",
        "description": (
            "Turn operational and customer data into reliable reports, "
            "dashboards, and recommendations."
        ),
        "responsibilities": (
            "Extract, clean, join, and validate data from multiple systems. "
            "Create dashboards and reports in Power BI or Tableau. Analyze "
            "trends, anomalies, and business performance."
        ),
        "required_qualifications": (
            "Bachelor's or master's degree in analytics, information science, "
            "statistics, or a related field. Strong SQL and spreadsheet skills."
        ),
        "preferred_qualifications": (
            "Python, Power BI, Tableau, PostgreSQL, and statistical modeling."
        ),
        "skills": (
            "SQL, Python, Excel, Power BI, Tableau, PostgreSQL, "
            "Data Analysis, Data Validation"
        ),
        "employment_type": "Full-time",
        "work_model": "Hybrid",
        "city": "Albany",
        "state": "New York",
        "country": "United States",
        "minimum_experience": 1,
        "maximum_experience": 3,
        "minimum_salary": 68000,
        "maximum_salary": 88000,
    },
    {
        "job_code": "KT-DATA-310",
        "title": "Cloud Data Engineer",
        "department": "Data Engineering",
        "description": (
            "Design scalable cloud data pipelines that make trusted data "
            "available for analytics and machine learning."
        ),
        "responsibilities": (
            "Build ETL and ELT pipelines, create cloud data models, monitor "
            "data quality, and deploy workflows on AWS and Databricks."
        ),
        "required_qualifications": (
            "Three or more years building production data pipelines. "
            "Advanced Python, SQL, Apache Spark, and AWS experience."
        ),
        "preferred_qualifications": (
            "Databricks, Delta Lake, Kafka, Airflow, dbt, and CI/CD."
        ),
        "skills": (
            "Python, SQL, PySpark, Databricks, Delta Lake, AWS, "
            "ETL, Apache Spark"
        ),
        "employment_type": "Full-time",
        "work_model": "Remote",
        "city": None,
        "state": None,
        "country": "United States",
        "minimum_experience": 3,
        "maximum_experience": 5,
        "minimum_salary": 105000,
        "maximum_salary": 135000,
    },
    {
        "job_code": "KT-QA-115",
        "title": "Quality Assurance Analyst",
        "department": "Quality Engineering",
        "description": (
            "Protect software quality by planning and executing functional, "
            "regression, integration, API, and UAT testing."
        ),
        "responsibilities": (
            "Create test cases, execute regression testing, investigate "
            "defects, verify fixes, support UAT, and report release risks."
        ),
        "required_qualifications": (
            "Two or more years of software testing experience and knowledge "
            "of test planning, defect tracking, APIs, and databases."
        ),
        "preferred_qualifications": (
            "Postman, SQL, Jira, Selenium, Playwright, and performance testing."
        ),
        "skills": (
            "Functional Testing, Regression Testing, API Testing, "
            "Postman, SQL, Jira, Selenium, UAT"
        ),
        "employment_type": "Full-time",
        "work_model": "Hybrid",
        "city": "Albany",
        "state": "New York",
        "country": "United States",
        "minimum_experience": 2,
        "maximum_experience": 4,
        "minimum_salary": 70000,
        "maximum_salary": 90000,
    },
    {
        "job_code": "KT-IT-122",
        "title": "IT Support Specialist",
        "department": "Corporate Technology",
        "description": (
            "Provide technical support for employee hardware, software, "
            "accounts, networking, Microsoft 365, and printers."
        ),
        "responsibilities": (
            "Manage ServiceNow tickets, troubleshoot user issues, provision "
            "accounts and devices, maintain assets, and escalate incidents."
        ),
        "required_qualifications": (
            "One or more years of help-desk, desktop-support, internship, "
            "or equivalent laboratory experience."
        ),
        "preferred_qualifications": (
            "ServiceNow, Active Directory, Intune, Exchange Online, "
            "CompTIA A+, and network-printer support."
        ),
        "skills": (
            "ServiceNow, Windows, Microsoft 365, Active Directory, "
            "Networking, Printers, Troubleshooting"
        ),
        "employment_type": "Full-time",
        "work_model": "Onsite",
        "city": "Albany",
        "state": "New York",
        "country": "United States",
        "minimum_experience": 1,
        "maximum_experience": 3,
        "minimum_salary": 55000,
        "maximum_salary": 70000,
    },
    {
        "job_code": "KT-BA-218",
        "title": "Business Systems Analyst",
        "department": "Enterprise Applications",
        "description": (
            "Connect business needs with practical technology solutions by "
            "gathering requirements and improving business processes."
        ),
        "responsibilities": (
            "Interview stakeholders, document requirements, analyze systems, "
            "support implementations, UAT, change requests, and Agile delivery."
        ),
        "required_qualifications": (
            "Two or more years of business analysis, systems analysis, "
            "requirements gathering, or related experience."
        ),
        "preferred_qualifications": (
            "Microsoft Power Platform, SQL, Jira, Visio, and API knowledge."
        ),
        "skills": (
            "Business Analysis, Requirements Gathering, SQL, Jira, "
            "UAT, Agile, Process Modeling"
        ),
        "employment_type": "Full-time",
        "work_model": "Hybrid",
        "city": "Albany",
        "state": "New York",
        "country": "United States",
        "minimum_experience": 2,
        "maximum_experience": 5,
        "minimum_salary": 78000,
        "maximum_salary": 102000,
    },
    {
        "job_code": "KT-AI-330",
        "title": "Machine Learning Engineer",
        "department": "Artificial Intelligence",
        "description": (
            "Build, evaluate, deploy, and monitor machine-learning and "
            "generative-AI systems."
        ),
        "responsibilities": (
            "Develop RAG pipelines, embeddings, vector search, model "
            "evaluations, AWS inference pipelines, and monitoring systems."
        ),
        "required_qualifications": (
            "Three or more years of Python and machine-learning experience "
            "with production model development."
        ),
        "preferred_qualifications": (
            "OpenAI APIs, vector databases, FastAPI, AWS, Docker, and MLOps."
        ),
        "skills": (
            "Python, Machine Learning, Generative AI, RAG, OpenAI, "
            "Vector Databases, FastAPI, AWS, Docker"
        ),
        "employment_type": "Full-time",
        "work_model": "Remote",
        "city": None,
        "state": None,
        "country": "United States",
        "minimum_experience": 3,
        "maximum_experience": 6,
        "minimum_salary": 115000,
        "maximum_salary": 150000,
    },
]


def seed_jobs() -> None:
    database = SessionLocal()

    try:
        added = 0
        skipped = 0

        for job_data in JOBS:
            existing_job = database.scalar(
                select(Job).where(
                    Job.job_code == job_data["job_code"]
                )
            )

            if existing_job is not None:
                print(
                    f"Skipped existing job: "
                    f"{job_data['job_code']}"
                )
                skipped += 1
                continue

            is_remote = (
                job_data["work_model"].lower()
                == "remote"
            )

            job = Job(
                company_id=COMPANY_ID,
                office_id=(
                    None
                    if is_remote
                    else ALBANY_OFFICE_ID
                ),
                application_url=(
                    "https://www.knowva.example/careers/"
                    f"{job_data['job_code']}"
                ),
                posted_at=POSTED_AT,
                closing_at=CLOSING_AT,
                status="open",
                **job_data,
            )

            database.add(job)
            added += 1

        database.commit()

        print(f"Added {added} jobs.")
        print(f"Skipped {skipped} existing jobs.")

    except Exception:
        database.rollback()
        raise
    finally:
        database.close()


if __name__ == "__main__":
    seed_jobs()