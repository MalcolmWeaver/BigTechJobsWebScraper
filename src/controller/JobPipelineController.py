from SiteFetcher import SiteFetcher
from src.storage.JobStorageInterface import JobStorageInterface
from JobSelector import JobSelector
from src.controller.ProfileCreator import ProfileCreator


class JobPipelineController():
    def __init__(self, fetcher: SiteFetcher, selector: JobSelector, storage: JobStorageInterface, profile_creator: ProfileCreator):
        self.fetcher = fetcher
        self.selector = selector
        self.storage = storage
        self.profile_creator = profile_creator

    def run_pipeline(self, city):
        self.fetcher.fetch_jobs(city)
        ## RUNS STOPS HERE
        profile = self.profile_creator.create_profile()
        suitable_jobs = self.selector.select_suitable_jobs(profile)
        return suitable_jobs

    ## TODO: Cron Job In this folder probably titled something like JobPipelineControllerJobs.py lol

