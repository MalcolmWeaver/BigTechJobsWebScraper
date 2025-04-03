from datetime import datetime
import structlog
from typing import List
from src.SiteFetcher import SiteFetcher
from src.models.job import JobPosting
from src.http.http_client import HttpClient
from bs4 import BeautifulSoup
import json
from src.storage.JobStorage import JobStorage

# Set up structured logger
logger = structlog.get_logger()

class MetaFetcher(SiteFetcher):
    def __init__(self):
        self.http_client = HttpClient()
        self.job_storage = JobStorage()

    def fetch_new_jobs(self, city: str):
        """
        The following logic is for job sites that have a terse search
        page and a job details page.

        """
        existing_job_ids = set(self.job_storage.get_job_ids())
        logger.info({"event": "existing_job_id_read", "count": len(existing_job_ids)})
        jobs_from_search_page = self.get_job_search_page(city)
        logger.info({"event": "fetched_jobs_from_search_page", "count": len(jobs_from_search_page)})
        new_jobs = [job for job in jobs_from_search_page if job.id not in existing_job_ids]
        logger.info({"event": "new_jobs_found", "count": len(new_jobs)})

        for job in new_jobs:
            job_with_details = self.get_job_with_details(job)
            if job_with_details:
                self.job_storage.update_or_create_jobs(job_with_details.id, job_with_details)
            else:
                logger.error({"event": "job_details_fetch_failed", "job_id": job.id})
        return new_jobs

    def refetch_jobs(self, city: str):
        """
        Refetches jobs from the search page and updates the database with new jobs
        """
        jobs_from_search_page = self.get_job_search_page(city)
        logger.info({"event": "fetched_jobs_from_search_page", "count": len(jobs_from_search_page)})

        self.job_storage.update_or_create_jobs(jobs_from_search_page)

        jobs_with_details = []
        for job in jobs_from_search_page:
            job_with_details = self.get_job_with_details(job)
            if job_with_details:
                # insert into db
                jobs_with_details.append(job_with_details)
                self.job_storage.update_or_create_jobs(jobs_with_details)
            else:
                logger.error({"event": "job_details_fetch_failed", "job_id": job.id})
                jobs_with_details.append(job)

        return True

    def get_job_search_page(self, city: str, page: int = 1, attempt: int = 0) -> List[JobPosting]:
        """
        Scrapes Meta's job board for basic listings using their GraphQL API
        """
        url, headers, payload = self._build_get_job_listings_request(city)
        response = self.http_client.request("POST", url, headers=headers, data=payload)

        if response.ok:
            parsed_job_listings = self._parse_get_job_listings(response, city)
            logger.info({"event": "job_listings_parsed", "count": len(parsed_job_listings)})
            return parsed_job_listings

        else:
            logger.error({"event": "job_listings_fetch_failed", "status_code": response.status_code})
            return []

    def get_job_with_details(self, job: JobPosting) -> JobPosting | None:
        """
        Fetches full job description and requirements
        """
        url, headers = self._build_get_job_with_details_request(job)
        response = self.http_client.request("GET", url, headers=headers)
        if response.ok:
            parsed_job_with_details = self._parse_get_job_with_details(job, response)
            logger.info({"event": "job_details_fetched", "job_id": parsed_job_with_details.id})
            return parsed_job_with_details
        else:
            print(f"Failed to fetch job details: {response.status_code}")
            return None


    def _parse_get_job_listings(self, response, city: str) -> List[JobPosting]:
        data = json.loads(response.text)
        try:
            raw_jobs = data["data"]["job_search"]
            assert isinstance(raw_jobs, list)
            # Filter to only include keys that exist in JobPosting
            job_model_fields = JobPosting.__annotations__.keys()
            jobs = []
            for job_data in raw_jobs:
                filtered_data = {
                    k: v for k, v in job_data.items() if k in job_model_fields
                }
                filtered_data["company"] = "meta"
                filtered_data["location"] = city
                filtered_data["posting_url"] = (
                    f"https://www.metacareers.com/jobs/{job_data['id']}"
                )
                jobs.append(JobPosting(**filtered_data))
            return jobs
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print(f"Error parsing job listings: {e}")
            return []

    def _build_get_job_listings_request(self, city: str):

        seattle_cities = ["Seattle, WA", "Bellevue, WA", "Redmond, WA"]
        austin_cities = ["Austin, TX"]
        bay_area_cities = ["Fremont, CA", "Menlo Park, CA", "Mountain View, CA", "Newark, CA", "Sunnyvale, CA", "Santa Clara, CA", "San Francisco, CA", "San Mateo, CA", "Foster City, CA"]
        bay_area_cities_set = set(bay_area_cities)
        bay_area_cities_set.add("bay area")

        if city.lower() in seattle_cities:
            search_input = {"offices": seattle_cities}
            city = "Seattle, WA"
        elif city.lower() in austin_cities:
            search_input = {"offices": austin_cities}
            city = "Austin, TX"
        elif city.lower() in bay_area_cities_set:
            search_input = {"offices": bay_area_cities}
            city = "Bay Area"
        else:
            logger.error({"event": "invalid_city", "city": city})
            raise ValueError(f"Invalid city: {city}. Should be one of: {seattle_cities}, {austin_cities}, {bay_area_cities}")

        url = "https://www.metacareers.com/graphql"

        # Define search parameters with all possible options
        search_input = {
            "q": None,
            "divisions": [],
            "offices": search_input["offices"],
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
                "Enterprise Engineering",
            ],
            "is_leadership": False,
            "is_remote_only": False,
            "sort_by_new": True,
            "results_per_page": None,
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
            "x-asbd-id": "129477",
        }

        # Full payload with all required parameters
        payload = {
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CareersJobSearchResultsQuery",
            "variables": json.dumps(variables),
            "doc_id": "9114524511922157",
        }

        return url, headers, payload


    def _build_get_job_with_details_request(self, job: JobPosting):
        url = f"https://www.metacareers.com/jobs/{job.id}/"

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://www.metacareers.com/jobs/?teams[0]=University%20Grad%20-%20Engineering%2C%20Tech%20%26%20Design&teams[1]=Software%20Engineering&teams[2]=Infrastructure&teams[3]=AR%2FVR&teams[4]=Artificial%20Intelligence&teams[5]=Data%20Center&teams[6]=Design%20%26%20User%20Experience&teams[7]=Enterprise%20Engineering&offices[0]=Seattle%2C%20WA&offices[1]=Bellevue%2C%20WA&offices[2]=Redmond%2C%20WA&offices[3]=Austin%2C%20TX&offices[4]=Temple%2C%20TX&offices[5]=Fremont%2C%20CA&offices[6]=Menlo%20Park%2C%20CA&offices[7]=Mountain%20View%2C%20CA&offices[8]=Newark%2C%20CA&offices[9]=Sunnyvale%2C%20CA&offices[10]=Santa%20Clara%2C%20CA&offices[11]=San%20Francisco%2C%20CA&offices[12]=San%20Mateo%2C%20CA&offices[13]=Foster%20City%2C%20CA&sort_by_new=true",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        }
        return url, headers

    def _parse_get_job_with_details(
        self, existing_job: JobPosting, response
    ) -> JobPosting:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", {"type": "application/ld+json"})
        if script_tag:
            data = json.loads(script_tag.string)
            # Map Meta's schema.org data to our JobPosting model
            new_data = {
                "title": data.get("title"),
                "description": data.get("description"),
                "responsibilities": (
                    data.get("responsibilities", "")
                ),
                "all_qualifications": (
                    "###".join([
                        f"{key}: {val}"
                        for key, val in data.items()
                        if "qualifi" in key.lower()
                    ])
                ),
                "company": "Meta",
                "id": data.get("id"),
                "posting_url": data.get("url"),
                "scraped_at": datetime.now().isoformat(),
            }

            new_data = {k: v for k, v in new_data.items() if v is not None}


            # Merge with existing job's data, preferring new data when available
            existing_data = {
                k: v for k, v in existing_job.__dict__.items() if v is not None
            }

            merged_data = {**existing_data, **new_data}

            return JobPosting(**merged_data)
        else:
            print("Data script tag not found")
            return None


if __name__ == "__main__":
    scraper = MetaFetcher()
    # jobs = scraper.get_job_listings()
    # print(f"Found {len(jobs)} jobs")
    # for job in jobs:
    #     print(job)

    # job = JobPosting(company="Meta", id="936067258115050", title="test")
    # print(scraper.get_job_with_details(job))

    val = scraper.refetch_jobs("Bay Area")
    print(val)
