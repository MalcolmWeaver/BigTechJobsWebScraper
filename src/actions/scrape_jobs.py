from enum import Enum
import time
from typing import List, Dict, Type, Optional
from src.models.job import JobPosting
from src.storage.jobs_db import JobsDatabase
from src.scrapers.meta import MetaScraper
from src.models.company import CompanyScrapers
import re
import requests
from src.models.resume import Resume
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

def filter_jobs_by_qualifications_text_based(jobs: List[JobPosting]) -> List[JobPosting]:
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


def filter_jobs_by_qualifications_ai_based(jobs: List[JobPosting], resume_text: Optional[str] = None) -> List[JobPosting]:
    """
    OLLAMA must be running locally to use this function.
    To run OLLAMA, run the following command:
    ollama run mistral

    kill with
    lsof -i :11434
    or
    pkill ollama

    Filter jobs using a local LLM via Ollama to determine if they're entry-level and a good match for the provided resume.

    Args:
        jobs: List of JobPosting objects to filter
        resume_text: Optional text content of the user's resume

    Returns:
        List[JobPosting]: Filtered list containing suitable positions
    """
    if not resume_text:
        return []

    OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
    db = JobsDatabase()
    matching_jobs = []

    for job in jobs:
        # Combine job details into a comprehensive description
        job_description = f"""
        Title: {job.title}
        Requirements: {' '.join(job.requirements)}
        Qualifications: {' '.join(job.extra_qualifications)}
        """

        # Construct the prompt for the LLM
        prompt = f"""
        Task: Analyze if the following job posting is suitable for an entry-level candidate
        and a good match for the candidate's resume. Consider:
        1. Would this be a realistic application for this candidate?
        2. Special emphasis that this does not expect a graduate degree.
        3. brief evaluation of the chances of being the most competitive candidate for this job.

        Job Details:
        {job_description}

        Qualifications:
        {job.extra_qualifications}

        Candidate's Resume:
        {resume_text}

        Make sure your answer includes "YES" if this is a good match for an entry-level candidate with this resume,
        and "NO" if it's not suitable. Limit yourself to 3 lines of text. Must be under 200 characters.
        """

        try:
            response = requests.post(
                OLLAMA_ENDPOINT,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                result = response.json()
                answer = result['response'].strip()
                print(f"OLLAMA RESPONSE FOR JOB {job.id}: {answer}")
                is_match = "YES" in answer.upper()
                # Update the database immediately for each job
                db.update_job_ai_match(CompanyScrapers(job.company), job.id, is_match, answer)
                if is_match:
                    matching_jobs.append(job)

        except Exception as e:
            print(f"Error processing job {job.id}: {str(e)}")
            continue

    return matching_jobs

def store_filtered_jobs_for_company(company_name: CompanyScrapers):
    db = JobsDatabase()
    jobs = db.get_jobs(company_name)
    filtered_jobs_text = filter_jobs_by_qualifications_text_based(jobs)
    for job in filtered_jobs_text:
        print(f"Filtered in: {job.title}, https://www.metacareers.com/jobs/{job.id}")
    # Update text_match status in database
    db.update_text_matches(company_name, [job.id for job in filtered_jobs_text])

    print("\n\n AI FILTERED JOBS \n\n this may take a while to run ...")
    filter_jobs_by_qualifications_ai_based(filtered_jobs_text, Resume().resume_text)
    print(f"Found {len(filtered_jobs_text)} matching jobs out of {len(jobs)} total jobs")

if __name__ == "__main__":
    company_name = input("Company name: ")
    company = CompanyScrapers(company_name.lower())
    scrape_jobs_for_company(company, force_refresh=False)
    store_filtered_jobs_for_company(company)
