from abc import ABC, abstractmethod
from typing import List
from src.models.job import JobPosting

class BaseScraper(ABC):
    """Base class that all company scrapers must implement"""

    @abstractmethod
    def get_job_listings(self) -> List[JobPosting]:
        """Get basic job listings (title, location, etc)"""
        pass

    @abstractmethod
    def get_job_with_details(self, job: JobPosting) -> JobPosting:
        """Enrich a job with its full description and requirements"""
        pass

    def is_overqualified(self, job: JobPosting, years_experience: int, skills: List[str]) -> bool:
        """
        Default implementation to check if overqualified.
        Can be overridden by specific companies if needed.
        """
        # Basic implementation - companies can override with specific logic
        required_years = job.required_years_experience or 0
        if years_experience > (required_years + 2):
            return True

        return False