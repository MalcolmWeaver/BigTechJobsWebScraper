import requests
from bs4 import BeautifulSoup
import time
import re
from utils import BaseJobsSiteScraper

def getNumberOfPages(queryUrl) -> int:
    try:
        apiResponse = requests.get(queryUrl)
    except:
        print(f"Could not get page for {queryUrl}")
        return 1
    apiResponseJson = apiResponse.json() 
    return ((int(apiResponseJson['hits'])-1) // 10) + 1
    # TODO:
    # try to use the "page-button" before "button circle right"?. 
    # If fail, return 1 or 0 if Sorry, there are no jobs that meet your criteria
    rightButtons = soup.find_all(class_ = "btn circle right")
    # assert(len(rightButtons) == 1)
    
    return  0

class Amazon(BaseJobsSiteScraper):
    def __init__(self, location="Seattle"):
        print(f"{self.__class__.__name__} Jobs Scraper")
        self.location = location
        self.outputFilename = f"{self.__class__.__name__}EntryLevelPositions{self.todayString}-{self.location}.txt"
        self.jobTitlesCacheFilename = f"{self.__class__.__name__}AllJobUrlsCache-{location}.txt"

        # put after jobsURLPrefix to get data from API
        self.apiCallPreface = "search.json?"

        # jobs query url is really an api call
        self.jobsQueryURL = self.getQueryURL(0)
        seattle_location = (
            "&loc_query=Greater+Seattle+Area%2C+WA%2C+United+States"
            "&latitude=&longitude=&loc_group_id=seattle-metro"
            "&invalid_location=false&country=&city=&region=&county="
        )

        bay_area_location = (
            "&loc_query=San+Francisco+Bay+Area%2C+CA%2C+United+States"
            "&latitude=&longitude=&loc_group_id=san-francisco-bay-area"
            "&invalid_location=false&country=&city=&region=&county="
        )

        austin_location = (
            "&loc_query=Austin%2C+TX%2C+United+States"
            "&latitude=30.26759&longitude=-97.74299&loc_group_id="
            "&invalid_location=false&country=USA&city=Austin&region=Texas&county=Travis"
        )

        self.locations["Seattle"] = seattle_location
        self.locations["Bay Area"] = bay_area_location
        self.locations["Austin"] = austin_location

        print("Base Query URL:", self.jobsQueryURL) 
        print("Output File:", self.outputFilename)  
    jobsURLPrefix = "https://www.amazon.jobs/en"
    
    def getQueryURL(self, offset=0):
        return (
                f"{self.jobsURLPrefix}/{self.apiCallPreface}"
                f"radius=24km"
                "&facets%5B%5D=normalized_country_code"
                "&facets%5B%5D=normalized_state_name"
                "&facets%5B%5D=normalized_city_name"
                "&facets%5B%5D=location"
                "&facets%5B%5D=business_category"
                "&facets%5B%5D=category"
                "&facets%5B%5D=schedule_type_id"
                "&facets%5B%5D=employee_class"
                "&facets%5B%5D=normalized_location"
                "&facets%5B%5D=job_function_id"
                "&facets%5B%5D=is_manager"
                "&facets%5B%5D=is_intern"
                f"&offset={offset}"
                "&result_limit=10"
                "&sort=recent"
                f"{self.locations[self.location]}"
            )
    def getJobPrintable(self, job):
        #TODO fix
        if "job_path" in job:
            jobId = f"https://www.amazon.jobs{job['job_path']}"
        else:
            return "Path not found in job"
        return f"{jobId}"
    
    def getAndCheckAllJobUrls(self, onlyNew=False, last5Jobs=[]):
        """
        """
        t0 = time.time()
        allJobUrls = []
        numPages = getNumberOfPages(self.jobsQueryURL)
        nEntryLevelPositions = 0
        """
        Only-New Logic: save the most recent 5 jobs. 
        If you one of those jobs (sorted by newest), you're done.
        This logic breaks down when all 5 of the most recent jobs are deleted, 
        but by then, you should probably rerun everything
        """

        # Naive Pagination: loop from 1 to numPages 
        #(this should be the number of pages of job results)
        for pageIdx in range(1, numPages+1):
            # loop through all the pages
            offset = (pageIdx - 1) * 10
            if (pageIdx + 1 ) % 10 == 0:
                print(f"\nProcessed {10*pageIdx} jobs. Time elapsed: {time.time() - t0}.")
                print(
                    f"Percent entry level: {nEntryLevelPositions / (len(allJobUrls)) * 100}% ({10*pageIdx} jobs). "
                    f"Percent complete ~ {(pageIdx+1) / (numPages+1) * 100}%. "
                    f"Expected time remaining: "
                    f"{(numPages - pageIdx) / (pageIdx + 1) * (time.time() - t0)/60} minutes\n"
                )
            
            currentQueryUrl = self.getQueryURL(offset) 
            # print(currentQueryUrl)
            try:
                apiResponse = requests.get(currentQueryUrl)
            except:
                print(f"Could not get page for {currentQueryUrl}")
                continue
            apiResponseJson = apiResponse.json()            

            newJobUrlsFromQuery = [self.getJobPrintable(job) for job in apiResponseJson["jobs"]]
            sweJobUrlsFromQuery = [
                job for job in apiResponseJson["jobs"] 
                    if job["job_category"] == "Software Development" or
                    job["job_family"] == "Software Engineering" or
            # ]
            # broader
                    job["job_family"] == "Hardware Engineering" or
                    job["job_category"] == "Hardware Engineering" or
                    job["job_family"] == "Data Engineering" or
                    job["job_family"] == "IT Application Engineering" or
                    job["job_family"] == "Research Science"
            ]

            if onlyNew:
                for idx, job in enumerate(newJobUrlsFromQuery):
                    if job in last5Jobs:
                        allJobUrls += newJobUrlsFromQuery[:idx]
                        return allJobUrls
                    
            nEntryLevelPositions += self.getEntryLevelPositionsFromList(
                sweJobUrlsFromQuery, 
                self.outputFilename, 
                writeTitle=(pageIdx == 1),
                printTimes=False,
                printResults=False
                )
            
            allJobUrls += newJobUrlsFromQuery
            
        t1 = time.time()
        print(
            f"Total number of {self.__class__.__name__}"
            f"jobs found: {len(allJobUrls)}. Elapsed time: {t1-t0}"
        )
        return allJobUrls

    def getJobData(self, job):
        return job

    def getJobTitle(self, job) -> str:
        return job['title']
    
    def getQualifications(self, job) -> list[str]:
        quals = []
        if "basic_qualifications" in job:
            quals.append(job["basic_qualifications"])
        if "preferred_qualifications" in job:
            quals.append(job["preferred_qualifications"])
        return quals
        
    def getEntryLevelPositions(self, onlyNew=False, isCached=False):
        """
        Retrieve all job URLs from the specified number of pages (all of them).
        """

        """
        Get the soup for the (first) page of query results.
        Get the number of pages for pagination.
        Optionally get all the job URLs from all pages and cache to a file, 
        or read from cached file.
        """

        if onlyNew:
            assert not isCached, "Cached data is not new data."

        allJobUrls = []
              
        print(
            f"Beginning to scan for entry level positions. "
            f"This may take a while. Check {self.outputFilename} for results..."
            )

        if onlyNew:
            # get number of pages until you hit a repeat of the last 5 jobs 
            # (should have already collected)
            f = open(self.jobTitlesCacheFilename, "r")
            allUrlsStr = f.read()
            allJobUrls = list(eval(allUrlsStr))
            f.close()

            newJobUrls = self.getAndCheckAllJobUrls(
                onlyNew=onlyNew, last5Jobs=allJobUrls[:5]
            )
            if newJobUrls == []:
                print("No new jobs found")
                return
            allJobUrls = newJobUrls
        else :
            # get number of pages for naive iteration
            allJobUrls = self.getAndCheckAllJobUrls(onlyNew=onlyNew)
        f = open(self.jobTitlesCacheFilename, "w")
        f.write(str(allJobUrls))
        print(f"{len(allJobUrls)} urls were cached")
        f.close()

if __name__ == "__main__":
    amazon = Amazon(location="Bay Area")
    amazon.getEntryLevelPositions(onlyNew=True, isCached=False)