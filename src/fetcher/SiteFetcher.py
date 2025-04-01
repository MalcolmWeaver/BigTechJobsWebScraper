from abc import ABC, abstractmethod
from src.storage.JobStorageInterface import JobStorageInterface

class SiteFetcher(JobStorageInterface):
    def __init__(self, storage: JobStorageInterface):
        self.storage = storage

    @abstractmethod
    def fetch_jobs(self, city):
        # Implementation to scrape jobs from a specific site
        # Store the results. May or may not implement pagination
        jobs = [] # Scraped jobs
        self.storage.store_jobs(jobs)
        return jobs