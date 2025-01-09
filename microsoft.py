import time
import requests
from utils import JobsScraperByApi

class Microsoft(JobsScraperByApi):
    locationSeg = "lc=United%20States"
    pageNum = 1
    jobId = 1691317
    locations = {
        "United States": "lc=United%20States",
        "Austin": "lc=Austin",
        "Seattle": "lc=Washington",
        "Bay Area": ("lc=San%20Francisco%2C%20California%2C%20United%20States"
                     "&lc=Mountain%20View%2C%20California%2C%20United%20States"
                     "&lc=Sunnyvale%2C%20California%2C%20United%20States"
                     "&lc=San%20Jose%2C%20California%2C%20United%20States&")
    }

    def __init__(self, location="Seattle"):
        super().__init__()
        self.outputFilename = f"{self.__class__.__name__}EntryLevelPositions{self.todayString}-{self.location}.txt"
        self.location = location
        self.locationSeg = self.locations[self.location]
        self.pageNum = 1
        self.jobsQueryURL = self.getJobSearchPage(self.locationSeg, self.pageNum)
        print(__class__.__name__ + " Jobs Scraper")
        print("First Search API url: " + self.jobsQueryURL)
        self.jobPageAPI = self.getJobUrl(self.jobId)
        print("First Page API url: " + self.jobPageAPI)

    def getJobSearchPage(self, locationSeg: str, pageNum: int) -> str:
        return (f"https://gcsservices.careers.microsoft.com/"
             f"search/api/v1/search?{locationSeg}&"
             f"p=Research%2C%20Applied%2C%20%26%20Data%20Sciences"
             f"&p=Software%20Engineering&rt=Individual%20Contributor"
             f"&l=en_us&pg={pageNum}&pgSz=20&o=Recent")

    def getJobUrl(self, job: int) -> str:
        return f"https://gcsservices.careers.microsoft.com/search/api/v1/job/{job}?lang=en_us"

    def getAllJobs(self, startPage, onlyNew=False, last5Jobs=[]) -> list[str]:
        """
        Given the url to the first search page, get all the job ids
        """
        t0 = time.time()
        try:
            result = requests.get(self.jobsQueryURL)
        except:
            print(f"Could not get page for {self.jobsQueryURL}")
            exit()
        resultJSON = result.json()

        # Naive pagination
        totalJobs = resultJSON["operationResult"]["result"]["totalJobs"]
        nPages = (totalJobs - 1) // 20 + 1
        allJobs = []

        for pageIdx in range(1, nPages + 1):
            currentPage = self.getJobSearchPage(self.locationSeg, pageIdx)
            # print("\nCurrent page: " + currentPage)
            try:
                currentResult = requests.get(currentPage)
            except:
                print(f"Could not get page for {self.jobsQueryURL}")
                exit()
            currentResultJSON = currentResult.json()
            jobs = currentResultJSON["operationResult"]["result"]["jobs"]
            # print(jobs)
            if onlyNew:
                for job in jobs:
                    if job["jobId"] in last5Jobs:
                        return allJobs
                    else:
                        allJobs += [job["jobId"]]
            else:
                allJobs += [job["jobId"] for job in jobs]

        print(f"Time elapsed to get all job IDs: {time.time() - t0}")

        return allJobs

    def getEntryLevelPositions(self, onlyNew=False, isCached=False):
        """

        """
        allJobUrls = []
        if isCached or onlyNew:
            # caching purposes (only about 0.1% change per hour)
            try:
                # get all job URLs from cached file
                f = open(self.jobTitlesCacheFilename, "r")
                allUrlsStr = f.read()
                allJobUrls = list(eval(allUrlsStr))
                # print(self.jobTitlesCacheFilename, allJobUrls)
                print(f"There are {len(allJobUrls)} cached urls from {self.jobsQueryURL}")
                f.close()
            except:
                print(f"Could not read cached file {self.jobTitlesCacheFilename}. Going to read from website")
                isCached = False

        if not isCached:
            if onlyNew:
                # get number of pages until you hit a repeat of the last 5 jobs (should have already collected)
                newJobUrls = self.getAllJobs(self.jobsQueryURL, onlyNew=onlyNew, last5Jobs=allJobUrls[:5])
                if newJobUrls == []:
                    print("No new jobs found")
                    return
                allJobUrls = newJobUrls


            else :
                # get number of pages for naive iteration
                allJobUrls = self.getAllJobs(self.jobsQueryURL, onlyNew=onlyNew)
            f = open(self.jobTitlesCacheFilename, "w")
            f.write(str(allJobUrls)+"\n")
            print(allJobUrls)
            print(f"{len(allJobUrls)} urls were cached from {self.jobsQueryURL}")
            f.close()

        print(f"Beginning to scan for entry level positions. This may take a while. Check {self.outputFilename} for results...")
        self.getEntryLevelPositionsFromList(allJobUrls, self.outputFilename)

    def getJobPrintable(self, job):
        return f"https://jobs.careers.microsoft.com/global/en/job/{job}"

    def getJobTitle(self, jobData) -> str:
        return jobData["title"]

    def getQualifications(self, jobData) -> str:
        return [jobData["qualifications"]]

    def getJobData(self, job):
        jobUrl = self.getJobUrl(job)
        try:
            result = requests.get(jobUrl)
        except:
            print(f"Could not get page for {jobUrl}")
            return None
        resultJSON = result.json()
        return resultJSON["operationResult"]["result"]

if __name__ == "__main__":
    microsoft = Microsoft()
    microsoft.getEntryLevelPositions(onlyNew=False, isCached=True)

