from src.storage.JobStorageInterface import JobStorageInterface
from src.models.job import JobPosting

class JobStorage(JobStorageInterface):
    def store_jobs(self, jobs):
        ## TODO: Implementation to store jobs (e.g., in a database)
        pass

    def get_jobs(self, filters=None):
        ## TODO: Implementation to retrieve jobs
        pass

    def update_job(self, job_id, updates):
        ## TODO: Implementation to update job details
        pass