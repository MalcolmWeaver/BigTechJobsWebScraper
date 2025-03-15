from datetime import datetime
from typing import List
from src.scrapers.base_scraper import BaseScraper
from src.models.job import JobPosting
from src.scrapers.http_client import HttpClient
from bs4 import BeautifulSoup
import json


class AppleScraper(BaseScraper):
    def __init__(self):
        self.http_client = HttpClient()

    def get_job_listings(self, page: int = 1, attempt: int = 0) -> List[JobPosting]:
        """
        Scrapes Apple's job board for basic listings using their GraphQL API
        """
        url, headers, _ = self.build_get_job_listings_request(page)
        response = self.http_client.request("GET", url, headers=headers)
        if response.ok:
            return self.parse_get_job_listings(response)
        else:
            if attempt < 3 and (
                response.status_code == 429
                or response.status_code == 400
                or response.status_code == 403
            ):
                self.http_client.new_tor_identity()
                return self.get_job_listings(attempt=attempt + 1)
            else:
                print(f"Error fetching job listings: {response.status_code}")
                return []

    def build_get_job_listings_request(self, page: int = 1):
        url = f"https://jobs.apple.com/en-us/search?location=washington-state1000+san-francisco-bay-area-SFMETRO+austin-metro-area-AUSMETRO+santa-clara-valley-cupertino-SCV&team=apps-and-frameworks-SFTWR-AF+cloud-and-infrastructure-SFTWR-CLD+core-operating-systems-SFTWR-COS+devops-and-site-reliability-SFTWR-DSR+engineering-project-management-SFTWR-EPM+information-systems-and-technology-SFTWR-ISTECH+machine-learning-and-ai-SFTWR-MCHLN+security-and-privacy-SFTWR-SEC+software-quality-automation-and-tools-SFTWR-SQAT+wireless-software-SFTWR-WSFT+machine-learning-infrastructure-MLAI-MLI+deep-learning-and-reinforcement-learning-MLAI-DLRL+natural-language-processing-and-speech-technologies-MLAI-NLP+computer-vision-MLAI-CV&page={page}"

        payload = {}
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://jobs.apple.com/en-us/details/200583029/software-engineer-siri-on-the-go-siri-and-information-intelligence?team=SFTWR",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Cookie": "jobs=2cc9a6ab2817a5fd727b4782c66405e6; AWSALBAPP-0=AAAAAAAAAAB+o5W4MjgIA3wuP8QA8wl0+K6CbRlQe020/c82wkfhHFnSwXSryZ8kZ6e3efKLOOMEfZouMJehsbJWD01trtrkhnBC6UscwdDLtEIQGyQ/aL4ZkGEIaQ+bMogpoUs4xJAYGQg=; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; NSESSIONID=s%3ATf9t2tEFM6AFySiwp4v6pxB0gOBDRE41.DNM%2BsyTwAU3Pp5AEg6j9Xv0FmRD%2BK9U4AIrxov3y1nY",
        }

        return url, headers, payload

    def parse_get_job_listings(self, response) -> JobPosting:
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all job listing elements
            job_elements = soup.find_all("a", class_="table--advanced-search__title")

            jobs = []
            for element in job_elements:
                job_data = {
                    "title": element.text,
                    "id": element["href"].split("/")[3],
                    "company": "apple",
                    "posting_url": f"https://jobs.apple.com{element['href']}",
                }
                jobs.append(JobPosting(**job_data))
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
        url = job.posting_url
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Cookie": "jobs=2cc9a6ab2817a5fd727b4782c66405e6; AWSALBAPP-0=AAAAAAAAAAB+o5W4MjgIA3wuP8QA8wl0+K6CbRlQe020/c82wkfhHFnSwXSryZ8kZ6e3efKLOOMEfZouMJehsbJWD01trtrkhnBC6UscwdDLtEIQGyQ/aL4ZkGEIaQ+bMogpoUs4xJAYGQg=; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; NSESSIONID=s%3ATf9t2tEFM6AFySiwp4v6pxB0gOBDRE41.DNM%2BsyTwAU3Pp5AEg6j9Xv0FmRD%2BK9U4AIrxov3y1nY",
        }
        return url, headers

    def parse_get_job_with_details(
        self, existing_job: JobPosting, response
    ) -> JobPosting:
        try:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all accordion sections
            accordion_sections = soup.find_all("div", class_="accordion-row")

            description = None
            requirements = []
            responsibilities = []
            extra_qualifications = []

            for section in accordion_sections:
                # Get the section ID which indicates the type of content
                section_id = section.get("id", "")

                if "description" in section_id.lower():
                    description_div = section.find("div", class_="jd__summary--main")
                    if description_div:
                        description = description_div.get_text(strip=True)

                elif (
                    "requirements" in section_id.lower()
                    or "qualifications" in section_id.lower()
                    or "education" in section_id.lower()
                ):
                    # Look for bullet points or paragraphs
                    items = section.find_all(["li", "p"])
                    for item in items:
                        text = item.get_text(strip=True)
                        if text:
                            requirements.append(text)

                elif (
                    "responsibilities" in section_id.lower()
                    or "role" in section_id.lower()
                ):
                    items = section.find_all(["li", "p"])
                    for item in items:
                        text = item.get_text(strip=True)
                        if text:
                            responsibilities.append(text)

            # Create updated job data
            job_data = {
                "id": existing_job.id,
                "company": "apple",
                "title": existing_job.title,
                "posting_url": existing_job.posting_url,
                "description": description,
                "requirements": requirements if requirements else None,
                "responsibilities": responsibilities if responsibilities else None,
                "extra_qualifications": (
                    requirements if requirements else None
                ),  # Using requirements as extra_qualifications
            }

            # Merge with existing job data
            existing_data = {
                k: v for k, v in existing_job.__dict__.items() if v is not None
            }
            merged_data = {**job_data, **existing_data}

            return JobPosting(**merged_data)

        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print(f"Error parsing job details: {e}")
            return existing_job

    def is_overqualified(
        self, job: JobPosting, years_experience: int, skills: List[str]
    ) -> bool:
        """
        Meta-specific logic for determining overqualification
        """
        # Override default implementation with Meta-specific logic
        if "new grad" in job.title.lower() and years_experience > 1:
            return True

        # Call parent implementation for basic checks
        return super().is_overqualified(job, years_experience, skills)
