from src.storage.JobStorageInterface import JobStorageInterface

class JobSelector:
    def __init__(self, storage: JobStorageInterface):
        self.storage = storage

    def select_suitable_jobs(self, user_profile):
        jobs = self.storage.get_jobs()
        suitable_jobs = []
        # Business logic to select jobs
        ## TODO: Implement logic to select jobs
        return suitable_jobs