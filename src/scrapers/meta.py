from datetime import datetime
from typing import List
from src.scrapers.base_scraper import BaseScraper
from src.models.job import JobPosting
from src.scrapers.http_client import HttpClient
from bs4 import BeautifulSoup
import json

class MetaScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://careers.meta.com/api/"
        self.http_client = HttpClient()
        # ... any auth or session setup

    def get_job_listings(self, attempt: int = 0) -> List[JobPosting]:
        """
        Scrapes Meta's job board for basic listings using their GraphQL API
        """
        url, headers, payload = self.build_get_job_listings_request()
        response = self.http_client.request("POST", url, headers=headers, data=payload)

        if response.ok:
          return self.parse_get_job_listings(response)
        else:
          if attempt < 3 and (response.status_code == 429 or response.status_code == 400 or response.status_code == 403):
              self.http_client.new_tor_identity()
              return self.get_job_listings(attempt=attempt + 1)
          else:
            print(f"Error fetching job listings: {response.status_code}")
            return []

    def build_get_job_listings_request(self):
        url = "https://www.metacareers.com/graphql"

        # Define search parameters with all possible options
        search_input = {
            "q": None,
            "divisions": [],
            "offices": [
                "Seattle, WA", "Bellevue, WA", "Redmond, WA",
                "Austin, TX", "Temple, TX",
                "Fremont, CA", "Menlo Park, CA", "Mountain View, CA",
                "Newark, CA", "Sunnyvale, CA", "Santa Clara, CA",
                "San Francisco, CA", "San Mateo, CA", "Foster City, CA"
            ],
            "roles": [],
            "leadership_levels": [],
            "saved_jobs": [],
            "saved_searches": [],
            "sub_teams": [],
            "teams": [
                "University Grad - Engineering, Tech & Design",
                "Software Engineering",
                "Infrastructure",
                "AR/VR",
                "Artificial Intelligence",
                "Data Center",
                "Design & User Experience",
                "Enterprise Engineering"
            ],
            "is_leadership": False,
            "is_remote_only": False,
            "sort_by_new": True,
            "results_per_page": None
        }

        variables = {"search_input": search_input}

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.metacareers.com",
            "referer": "https://www.metacareers.com/jobs/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-fb-friendly-name": "CareersJobSearchResultsQuery",
            "x-asbd-id": "129477"
        }

        # Full payload with all required parameters
        payload = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CareersJobSearchResultsQuery",
            "variables": json.dumps(variables),
            "doc_id": "9114524511922157"
        }

        return url, headers, payload

    def parse_get_job_listings(self, response) -> JobPosting:
      data = json.loads(response.text)
      try:
          raw_jobs = data["data"]["job_search"]
          assert isinstance(raw_jobs, list)
          # Filter to only include keys that exist in JobPosting
          job_model_fields = JobPosting.__annotations__.keys()
          jobs = []
          for job_data in raw_jobs:
              filtered_data = {k: v for k, v in job_data.items() if k in job_model_fields}
              filtered_data["company"] = "Meta"
              filtered_data["posting_url"] = f"https://www.metacareers.com/jobs/{job_data['id']}"
              jobs.append(JobPosting(**filtered_data))
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
        print(f"made request to {url}") # TODO: set up logging/monitoring
        if response.ok:
            return self.parse_get_job_with_details(job, response)
        else:
          print(f"Failed to fetch job details: {response.status_code}")
          return None

    def build_get_job_with_details_request(self, job: JobPosting):
        url = f"https://www.metacareers.com/jobs/{job.id}/"

        headers = {
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
          'accept-language': 'en-US,en;q=0.9',
          'cache-control': 'no-cache',
          'pragma': 'no-cache',
          'priority': 'u=0, i',
          'referer': 'https://www.metacareers.com/jobs/?teams[0]=University%20Grad%20-%20Engineering%2C%20Tech%20%26%20Design&teams[1]=Software%20Engineering&teams[2]=Infrastructure&teams[3]=AR%2FVR&teams[4]=Artificial%20Intelligence&teams[5]=Data%20Center&teams[6]=Design%20%26%20User%20Experience&teams[7]=Enterprise%20Engineering&offices[0]=Seattle%2C%20WA&offices[1]=Bellevue%2C%20WA&offices[2]=Redmond%2C%20WA&offices[3]=Austin%2C%20TX&offices[4]=Temple%2C%20TX&offices[5]=Fremont%2C%20CA&offices[6]=Menlo%20Park%2C%20CA&offices[7]=Mountain%20View%2C%20CA&offices[8]=Newark%2C%20CA&offices[9]=Sunnyvale%2C%20CA&offices[10]=Santa%20Clara%2C%20CA&offices[11]=San%20Francisco%2C%20CA&offices[12]=San%20Mateo%2C%20CA&offices[13]=Foster%20City%2C%20CA&sort_by_new=true',
          'sec-ch-ua': '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        }
        return url, headers

    def parse_get_job_with_details(self, existing_job: JobPosting, response) -> JobPosting:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if script_tag:
            data = json.loads(script_tag.string)

            # Map Meta's schema.org data to our JobPosting model
            mapped_data = {
                'title': data.get('title'),
                'description': data.get('description'),
                'responsibilities': data.get('responsibilities', '').split(';') if data.get('responsibilities') else None,
                'requirements': data.get('qualifications', '').split(';') if data.get('qualifications') else None,
                'extra_qualifications': [qual for key, val in data.items() if 'qualification' in key.lower() and val for qual in val.split(';')] if any('qualification' in key.lower() for key in data.keys()) else None,
                'posted_date': datetime.fromisoformat(data['datePosted']) if data.get('datePosted') else None,
                'company': 'Meta',
                'id': data.get('id'),
                'posting_url': data.get('url')
            }



            # Merge with existing job's data, preferring new data when available
            existing_data = {k: v for k, v in existing_job.__dict__.items() if v is not None}
            merged_data = {**mapped_data, **existing_data}

            return JobPosting(**merged_data)
        else:
          print("Data script tag not found")
          return None

    def is_overqualified(self, job: JobPosting, years_experience: int, skills: List[str]) -> bool:
        """
        Meta-specific logic for determining overqualification
        """
        # Override default implementation with Meta-specific logic
        if "new grad" in job.title.lower() and years_experience > 1:
            return True

        # Call parent implementation for basic checks
        return super().is_overqualified(job, years_experience, skills)


if __name__ == "__main__":
    scraper = MetaScraper()
    # jobs = scraper.get_job_listings()
    # print(f"Found {len(jobs)} jobs")
    # for job in jobs:
    #     print(job)
    job = JobPosting(company='Meta', id='936067258115050', title="test")
    print(scraper.get_job_with_details(job))
