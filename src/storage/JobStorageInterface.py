# from . import JobStorage

class JobStorageInterface:
    def insert_jobs(self, jobs):
        # JobStorage.insert_jobs(jobs)
        raise NotImplementedError

    def get_jobs(self, filters=None):
        # JobStorage.get_jobs(filters)
        raise NotImplementedError

    def update_job(self, job_id, updated_job):
        # JobStorage.update_job(job_id, updated_job)
        raise NotImplementedError