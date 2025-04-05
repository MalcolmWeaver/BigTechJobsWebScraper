import structlog
from src.models.job import JobPosting
from src.storage.JobStorageInterface import JobStorageInterface
import sqlite3
import json
from pathlib import Path
from datetime import datetime

logger = structlog.get_logger(__name__)

class JobStorage(JobStorageInterface):
    def __init__(self, db_path: str = "data/JobsPostings.db"):
        self.db_path = Path(db_path)
        self.initialize_database()

    def initialize_database(self):
        """Create the database and tables if they don't exist"""
        logger.info({"event": "job_storage.initialize_database", "db_path": self.db_path})
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_postings (
                    id TEXT,
                    company TEXT,
                    title TEXT NOT NULL,
                    posting_url TEXT,
                    description TEXT,
                    responsibilities TEXT,
                    all_qualifications TEXT,
                    scraped_at TIMESTAMP,
                    is_match BOOLEAN DEFAULT FALSE,
                    match_reason TEXT,
                    generated_cv TEXT,
                    location TEXT,
                    PRIMARY KEY (id, company)
                )
            """)
            conn.commit()

    def insert_jobs(self, jobs):
        """Store job postings in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for job in jobs:
                # Convert the domain object to a dict representation for storage
                job_dict = self._to_storage_model(job)

                cursor.execute("""
                    INSERT OR REPLACE INTO job_postings (
                        id, company, title, posting_url, description,
                        responsibilities, all_qualifications, scraped_at, location
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_dict.get("id"),
                    job_dict.get("company"),
                    job_dict.get("title"),
                    job_dict.get("posting_url"),
                    job_dict.get("description"),
                    job_dict.get("responsibilities"),
                    job_dict.get("all_qualifications"),
                    job_dict.get("scraped_at"),
                    job_dict.get("location")
                ))
            conn.commit()
            logger.info({"event": "job_storage.store_jobs", "num_jobs": len(jobs)})

    def get_jobs(self, filters=None):
        """Retrieve jobs from the database with optional filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM job_postings"
            params = []

            if filters:
                where_clauses = []
                if "id" in filters:
                    where_clauses.append("id = ?")
                    params.append(filters["id"])
                if "company" in filters:
                    where_clauses.append("company = ?")
                    params.append(filters["company"])
                if "location" in filters:
                    where_clauses.append("location = ?")
                    params.append(filters["location"])
                if "title" in filters:
                    where_clauses.append("title LIKE ?")
                    params.append(f"%{filters['title']}%")
                if "match_reason" in filters and filters["match_reason"] == None:
                    where_clauses.append('match_reason = ""')
                if "description" in filters:
                    if filters["description"] == True:
                        where_clauses.append('description != ""')
                    elif filters["description"] == False:
                        where_clauses.append('description = ""')

                # Add more filters as needed

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            logger.info({"event": "job_storage.get_jobs", "num_jobs": len(rows)})

            # Convert database rows to domain objects
            return [self._to_domain_model(dict(row)) for row in rows]

    def get_job_ids(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM job_postings")
            return [row[0] for row in cursor.fetchall()]


    def update_job(self, job_id: str, updates: JobPosting | dict):
        """Update job details in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if isinstance(updates, JobPosting):
                # Convert JobPosting to dict and filter out None values
                job_dict = self._to_storage_model(updates)
            else:
                job_dict = updates

            job_dict = {k: v for k, v in job_dict.items() if v is not None}
            if not job_dict:
                return False

            set_clauses = []
            params = []

            for key, value in job_dict.items():
                if key != 'id':  # Skip id since it's used in WHERE clause
                    set_clauses.append(f"{key} = ?")
                    if key in ["responsibilities", "requirements", "all_qualifications", "teams", "locations"]:
                        params.append(json.dumps(value))
                    else:
                        params.append(value)

            # Add WHERE clause parameters
            params.extend([job_id])

            cursor.execute(f"""
                UPDATE job_postings
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, params)

            conn.commit()

            logger.info({"event": "job_storage.job_updated", "job_id": job_id, "updates": updates})

            self.get_jobs(filters={"id": job_id})
            return cursor.rowcount > 0

    def update_or_create_jobs(self, jobs: list[JobPosting]):
        """Update or create a job in the database"""

        existing_job_ids = set(self.get_job_ids())
        new_jobs = [job for job in jobs if job.id not in existing_job_ids]
        old_jobs = [job for job in jobs if job.id in existing_job_ids]

        self.insert_jobs(new_jobs)
        for job in old_jobs:
            self.update_job(job.id, job)

    def _to_storage_model(self, job_posting):
        """Convert a domain JobPosting object to a dictionary for storage"""
        # Get all attributes from the job_posting object
        return vars(job_posting)

    def _to_domain_model(self, row_dict):
        """Convert a database row dictionary to a domain object dict
        The caller will instantiate the actual domain object"""
        # Convert any JSON strings back to Python objects
        for key in ["responsibilities", "requirements", "all_qualifications", "teams", "locations"]:
            if key in row_dict and isinstance(row_dict[key], str):
                try:
                    row_dict[key] = json.loads(row_dict[key])
                except json.JSONDecodeError:
                    pass

        return JobPosting(**row_dict)