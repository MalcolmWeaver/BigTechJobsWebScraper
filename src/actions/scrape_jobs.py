from enum import Enum
import time
from typing import List, Dict, Type
from src.models.job import JobPosting
from src.storage.jobs_db import JobsDatabase
from src.scrapers.meta import MetaScraper
from src.models.company import CompanyScrapers
import re

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

def filter_jobs_by_qualifications(jobs: List[JobPosting]) -> List[JobPosting]:
    """
    Filter jobs to only include entry-level positions based on qualifications.

    Args:
        jobs: List of JobPosting objects to filter

    Returns:
        List[JobPosting]: Filtered list containing only entry-level positions
    """
    years_pattern = re.compile(
        r'(?:(\d+)(?:\s*[-+]?\s*(?:years?|yrs?|y)|(?:[^\w\d]{1,5})(?:years?|yrs?|yr)))'
        r'|'
        r'(?:(one|two|three|four|five|six|seven|eight|nine|ten)(?:\+|&#43;)?\s*(?:&nbsp;|\s)*(?:year|yr)s?)'
    )

    includes_grad = re.compile(r'(?:M\.S\.?|Ph\.?\s?D\.?|PhD|[Mm]aster(?:[\\u0027]|\')?s|[Dd]octorate)(?:\s|\(|\)|$)')
    includes_bachelors = re.compile(r'(BA|BS|Bachelor|BACHELOR)')

    leadership_pattern = re.compile(r'(?:[Ll]ead(?:er|ership)?|[Mm]anager(?:ial)?|[Dd]irect(?:or|ing))')

    research_pattern = re.compile(r'(?:[Rr]esearch|[Dd]ata\s+[Ss]cientist)')

    def is_entry_level(job: JobPosting, strict: bool = False) -> bool:
        # Combine all relevant text fields for checking
        if strict:
            qualifications = ' '.join(job.extra_qualifications).lower()
        else:
            qualifications = ' '.join(job.requirements).lower()

        title = job.title

        # Check for graduate degree in title first
        if includes_grad.search(title):
            # print(f"DEBUG: Filtered out: Graduate degree found in title")
            return False

        title = title.lower()

        # Check for years of experience
        if years_pattern.search(qualifications):
            # print(f"DEBUG: Filtered out: Years of experience found")
            return False

        # Check for graduate degree requirements
        if strict and includes_grad.search(qualifications):
            # print(f"DEBUG: Filtered out: Strict mode - Graduate degree requirements found")
            return False

        if not strict and includes_grad.search(qualifications) and not includes_bachelors.search(qualifications):
            # print(f"DEBUG: Filtered out: Non-strict mode - Graduate degree only requirements found")
            return False

        if strict and research_pattern.search(title):
            # print(f"DEBUG: Filtered out: Research role found")
            return False

        # Check for leadership requirements
        if leadership_pattern.search(title):
            # print(f"DEBUG: Filtered out: Leadership role found")
            return False

        # print(f"DEBUG: Filtered in: {qualifications}")
        return True

    # return [job for job in jobs if is_entry_level(job)]
    return [job for job in jobs if is_entry_level(job, strict=True)]
    # Get both strict and non-strict filtered jobs
    # strict_filtered = [job for job in jobs if is_entry_level(job, strict=True)]
    # non_strict_filtered = [job for job in jobs if is_entry_level(job, strict=False)]

    # # Find jobs that are in non-strict but not in strict filtering
    # difference = [job for job in non_strict_filtered if job not in strict_filtered]

    return difference



def store_filtered_jobs_for_company(company_name: CompanyScrapers):
    db = JobsDatabase()
    jobs = db.get_jobs(company_name) # TODO: filter by company name (currently meta is Meta not META)
    filtered_jobs = filter_jobs_by_qualifications(jobs)
    # print(f"filtered_jobs: {[f"https://www.metacareers.com/jobs/{job.id}" for job in filtered_jobs]}")
    for job in filtered_jobs:
        print(f"Filtered in: {job.title}, https://www.metacareers.com/jobs/{job.id}")
    # db = JobsDatabase()
    # db.store_jobs(filtered_jobs, company_name)

if __name__ == "__main__":
    # scrape_jobs_for_company(CompanyScrapers.META)
    store_filtered_jobs_for_company(CompanyScrapers.META)