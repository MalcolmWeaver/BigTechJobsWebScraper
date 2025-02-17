from enum import Enum
import time
from typing import List, Dict, Type
from src.models.job import JobPosting
from src.storage.jobs_db import JobsDatabase
from src.scrapers.meta import MetaScraper
from src.models.company import CompanyScrapers
# Define a mapping of company names to scraper classes
COMPANY_SCRAPER_MAP: Dict[CompanyScrapers, Type] = {
    CompanyScrapers.META: MetaScraper,
    # CompanyScrapers.GOOGLE: GoogleScraper,
    # CompanyScrapers.AMAZON: AmazonScraper,
}

def get_scraper_for_company(company_name: CompanyScrapers):
    try:
        scraper_class = COMPANY_SCRAPER_MAP[company_name]
        return scraper_class()
    except KeyError:
        raise ValueError(f"Scraper not implemented for company: {company_name}")

def scrape_jobs_for_company(
    company_name: CompanyScrapers,
    force_refresh: bool = False,
    batch_size: int = 10,
    rate_limit_delay: float = 0.0  # Delay in seconds between API calls
):
    scraper = get_scraper_for_company(company_name)
    job_listings = scraper.get_job_listings()
    db = JobsDatabase()

    if force_refresh:
        jobs_to_process = job_listings
        print(f"Force refreshing all {len(job_listings)} jobs")
    else:
        existing_ids = set(job.id for job in db.get_jobs(company_name))
        jobs_to_process = [job for job in job_listings if job.id not in existing_ids]
        print(f"Found {len(jobs_to_process)} new jobs out of {len(job_listings)} total listings")

    processed_jobs = []

    for i, job in enumerate(jobs_to_process):
      print(f"Processing job {job.id}")
      job_with_details = scraper.get_job_with_details(job)
      if job_with_details:
          processed_jobs.append(job_with_details)
          db.store_job(job_with_details, company_name)

    return processed_jobs


def filter_jobs_by_qualifications(jobs: List[JobPosting]):
    # regex on description
    # regex on requirements
    # regex on team
    # regex on level
    # regex on title
    pass

if __name__ == "__main__":
    scrape_jobs_for_company(CompanyScrapers.META)
