from datetime import datetime
from typing import List
from src.scrapers.base_scraper import BaseScraper
from src.models.job import JobPosting
from src.scrapers.http_client import HttpClient
from bs4 import BeautifulSoup
import json


class MicrosoftScraper(BaseScraper):
    def __init__(self):
        self.http_client = HttpClient()

    def get_job_listings(self, page: int = 1, attempt: int = 0) -> List[JobPosting]:
        """
        Scrapes Microsoft's job board for basic listings using their GraphQL API
        """
        print(f"Fetching page {page}")
        url, headers, payload = self.build_get_job_listings_request(page)
        response = self.http_client.request("GET", url, headers=headers, data=payload)

        if response.ok:
            return self.parse_get_job_listings(response)
        else:
            if attempt < 3 and (
                response.status_code == 429
                or response.status_code == 400
                or response.status_code == 403
            ):
                self.http_client.new_tor_identity()
                return self.get_job_listings(page=page, attempt=attempt + 1)
            else:
                print(f"Error fetching job listings: {response.status_code}")
                return []

    def build_get_job_listings_request(self, page: int = 1):
        url = f"https://gcsservices.careers.microsoft.com/search/api/v1/search?lc=Washington%2C%20United%20States&lc=Austin%2C%20Texas%2C%20United%20States&lc=California%2C%20United%20States&p=Data%20Center&p=Engineering&p=Security%20Engineering&p=Software%20Engineering&rt=Individual%20Contributor&l=en_us&pg={page}&pgSz=50&o=Relevance&flt=true"

        payload = {}
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.5",
            "authorization": "Bearer undefined",
            "cache-control": "no-cache",
            "origin": "https://jobs.careers.microsoft.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://jobs.careers.microsoft.com/",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "x-correlationid": "e5e9b321-edf0-8c62-e203-2d0ca040b48f",
            "x-subcorrelationid": "ee0aa760-3f48-6d04-45df-0e29b8659bd0",
        }

        return url, headers, payload

    def parse_get_job_listings(self, response) -> List[JobPosting]:
        data = json.loads(response.text)
        try:
            raw_jobs = data["operationResult"]["result"]["jobs"]
            assert isinstance(raw_jobs, list)
            jobs = []
            for job_data in raw_jobs:
                job = {
                    "company": "microsoft",
                    "title": job_data["title"],
                    "id": job_data["jobId"],
                    "posting_url": f"https://jobs.careers.microsoft.com/global/en/job/{job_data['jobId']}",
                    "posted_date": datetime.fromisoformat(job_data["postingDate"]),
                    "description": job_data["properties"]["description"],
                    "locations": job_data["properties"]["locations"],
                    "location": job_data["properties"]["primaryLocation"],
                }
                jobs.append(JobPosting(**job))
            return jobs
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print(f"Error parsing job listings: {e}")
            return []

    def get_job_with_details(self, job: JobPosting) -> JobPosting | None:
        """
        Fetches full job description and requirements
        """
        url, headers = self.build_get_job_with_details_request(job)
        response = self.http_client.request("GET", url, headers=headers)
        print(f"made request to {url}")  # TODO: set up logging/monitoring
        if response.ok:
            return self.parse_get_job_with_details(job, response)
        else:
            print(f"Failed to fetch job details: {response.status_code}")
            return None

    def build_get_job_with_details_request(self, job: JobPosting):
        url = f"https://gcsservices.careers.microsoft.com/search/api/v1/job/{job.id}?lang=en_us"

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.5",
            "authorization": "Bearer undefined",
            "cache-control": "no-cache",
            "origin": "https://jobs.careers.microsoft.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://jobs.careers.microsoft.com/",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "x-correlationid": "e5e9b321-edf0-8c62-e203-2d0ca040b48f",
            "x-subcorrelationid": "1046a390-3dc3-a736-6fab-4872faf7f219",
        }
        return url, headers

    def parse_get_job_with_details(
        self, existing_job: JobPosting, response
    ) -> JobPosting:
        data = json.loads(response.text)["operationResult"]["result"]
        if not isinstance(data, dict):
            print("Data is not a dictionary")
            return None

        # Map Microsoft's schema.org data to our JobPosting model
        description = None
        responsibilities = None
        locations = None
        location = None
        extra_qualifications = None
        try:
            responsibilities = [data["responsibilities"]]
        except KeyError as e:
            print(f"KeyError Getting Responsibilities: {e} for job {existing_job.id}")
        try:
            description = json.dumps(data["description"])
        except KeyError as e:
            print(f"KeyError Getting Description: {e} for job {existing_job.id}")
        try:
            extra_qualifications = (
                [
                    str(val)
                    for key, val in data.items()
                    if "qualification" in key.lower() or "requirement" in key.lower()
                ]
                if any(
                    "qualification" in key.lower() or "requirement" in key.lower()
                    for key in data.keys()
                )
                else None
            )
        except KeyError as e:
            print(f"KeyError Getting Qualifications: {e} for job {existing_job.id}")

        try:
            locations = json.dumps(data["workLocations"])
            location = json.dumps(data["primaryWorkLocation"])
        except KeyError as e:
            print(f"KeyError Getting Locations: {e} for job {existing_job.id}")

        mapped_data = {
            "company": "microsoft",
            "description": description,
            "extra_qualifications": extra_qualifications,
            "responsibilities": responsibilities,
            "locations": locations,
            "location": location,
        }
        # Merge with existing job's data, preferring new data when available
        existing_data = {
            k: v for k, v in existing_job.__dict__.items() if v is not None
        }
        merged_data = {**mapped_data, **existing_data}

        return JobPosting(**merged_data)

    def is_overqualified(
        self, job: JobPosting, years_experience: int, skills: List[str]
    ) -> bool:
        """
        Microsoft-specific logic for determining overqualification
        """
        # Override default implementation with Microsoft-specific logic
        if "new grad" in job.title.lower() and years_experience > 1:
            return True

        # Call parent implementation for basic checks
        return super().is_overqualified(job, years_experience, skills)


if __name__ == "__main__":
    scraper = MicrosoftScraper()
    # jobs = scraper.get_job_listings()
    # print(f"Found {len(jobs)} jobs")
    # for job in jobs:
    #     print(job)
    job = JobPosting(company="Microsoft", id="936067258115050", title="test")
    print(scraper.get_job_with_details(job))
