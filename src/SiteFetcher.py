from abc import abstractmethod
from src.storage.JobStorageInterface import JobStorageInterface

class SiteFetcher(JobStorageInterface):
    def __init__(self, storage: JobStorageInterface):
        self.storage = storage

    @abstractmethod
    def fetch_new_jobs(self, city):
        raise NotImplementedError("Subclass must implement fetch_new_jobs")

    @abstractmethod
    def refetch_jobs(self, city):
        raise NotImplementedError("Subclass must implement refetch_jobs")



