from datetime import datetime
import sqlite3
from pathlib import Path
from typing import List, Optional
from src.models.job import JobPosting
from src.models.company import CompanyScrapers

class JobsDatabase:
    def __init__(self, db_path: str = "data/jobs.db"):
        self.db_path = Path(db_path)
        self.initialize_database()

    def initialize_database(self):
        """Create the database and tables if they don't exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT,
                    company TEXT,
                    title TEXT NOT NULL,
                    location TEXT,
                    locations TEXT, /* Stored as JSON array */
                    posting_url TEXT,
                    posted_date TIMESTAMP,
                    description TEXT,
                    requirements TEXT, /* Stored as JSON array */
                    salary_range TEXT,
                    team TEXT,
                    teams TEXT, /* Stored as JSON array */
                    level TEXT,
                    responsibilities TEXT, /* Stored as JSON array */
                    extra_qualifications TEXT, /* Stored as JSON array */
                    scraped_at TIMESTAMP,
                    PRIMARY KEY (id, company)
                )
            """)
            conn.commit()

    def update_job(self, job: JobPosting, company_name: CompanyScrapers) -> bool:
        """
        Update an existing job in the database
        Returns True if job was updated, False if job didn't exist
        """
        import json

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if job exists
            cursor.execute(
                "SELECT 1 FROM jobs WHERE id = ? AND company = ?",
                (job.id, job.company)
            )

            if not cursor.fetchone():
                return False

            cursor.execute("""
                UPDATE jobs SET
                title = ?,
                location = ?,
                locations = ?,
                posting_url = ?,
                posted_date = ?,
                description = ?,
                requirements = ?,
                salary_range = ?,
                team = ?,
                teams = ?,
                level = ?,
                responsibilities = ?,
                extra_qualifications = ?,
                scraped_at = ?
                WHERE id = ? AND company = ?
            """, (
                job.title,
                job.location,
                json.dumps(job.locations) if job.locations else None,
                job.posting_url,
                job.posted_date.isoformat() if job.posted_date else None,
                job.description,
                json.dumps(job.requirements) if job.requirements else None,
                job.salary_range,
                job.team,
                json.dumps(job.teams) if job.teams else None,
                job.level,
                json.dumps(job.responsibilities) if job.responsibilities else None,
                json.dumps(job.extra_qualifications) if job.extra_qualifications else None,
                datetime.now(),
                job.id,
                job.company
            ))
            conn.commit()
            return True

    def store_job(self, job: JobPosting, company_name: CompanyScrapers):
        """Store a single job in the database. If job exists, it will be replaced."""
        import json

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO jobs
                (id, company, title, location, locations, posting_url, posted_date,
                description, requirements, salary_range, team, teams, level,
                responsibilities, extra_qualifications, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                company_name.value,
                job.title,
                job.location,
                json.dumps(job.locations) if job.locations else None,
                job.posting_url,
                job.posted_date.isoformat() if job.posted_date else None,
                job.description,
                json.dumps(job.requirements) if job.requirements else None,
                job.salary_range,
                job.team,
                json.dumps(job.teams) if job.teams else None,
                job.level,
                json.dumps(job.responsibilities) if job.responsibilities else None,
                json.dumps(job.extra_qualifications) if job.extra_qualifications else None,
                datetime.now()
            ))
            conn.commit()

    def get_jobs(self, company_name: Optional[CompanyScrapers] = None, days_old: Optional[int] = None) -> List[JobPosting]:
        """Retrieve jobs from the database with optional filtering"""
        import json

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM jobs"
            params = []

            if company_name or days_old:
                query += " WHERE"
                conditions = []

                if company_name:
                    conditions.append("company = ?")
                    params.append(company_name.value)

                if days_old:
                    conditions.append("scraped_at >= datetime('now', ?)")
                    params.append(f'-{days_old} days')

                query += " " + " AND ".join(conditions)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [JobPosting(
                id=row[0],
                company=row[1],
                title=row[2],
                location=row[3],
                locations=json.loads(row[4]) if row[4] else None,
                posting_url=row[5],
                posted_date=datetime.fromisoformat(row[6]) if row[6] else None,
                description=row[7],
                requirements=json.loads(row[8]) if row[8] else None,
                salary_range=row[9],
                team=row[10],
                teams=json.loads(row[11]) if row[11] else None,
                level=row[12],
                responsibilities=json.loads(row[13]) if row[13] else None,
                extra_qualifications=json.loads(row[14]) if row[14] else None
            ) for row in rows]