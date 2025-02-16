import os
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

class BaseJobsSiteScraper:
    def __init__(self, location):
        super().__init__()
        print(f"{self.__class__.__name__} Jobs Scraper")
        self.location = location
        print(f"Location: {self.location}")
        self.outputFilename = os.path.join("job_outputs", f"{self.__class__.__name__}EntryLevelPositions{self.todayString}-{self.location}.txt")
        self.jobTitlesCacheFilename = os.path.join("job_caches", f"{self.__class__.__name__}AllJobsCache-{self.location}.txt")
        self.location = location
        self.jobsQueryURL = self.getQueryURL(location)
        self.jobsQueryURL = f"{self.jobsURLPrefix}/search?base_query=software&{self.locations[self.location]}"

    todayString = datetime.today().strftime('%Y-%m-%d')
    jobsURLPrefix = ""
    locations = {
        "Seattle": "",
        "Austin": "",
        "Bay Area": "",
    }
    sortSeg = ""

    def getQueryURL(self, location, offset=0):
        raise NotImplementedError(self)

    def getAllJobs(self, startPage, onlyNew=False, last5Jobs=[]) -> list[str]:
        raise NotImplementedError(self)

    def getJobUrl(self, job):
        return f"{self.jobsURLPrefix}{job}"

    def getJobTitle(self, soup) -> str:
        raise NotImplementedError(self)

    def getQualifications(self, soup) -> list[str]:
        raise NotImplementedError(self)

    def getJobData(self):
        raise NotImplementedError(self)

    def jobTitleIsEntryLevel(self, title: str) -> bool:
        """
        Check if the title could be for an entry level job.

        Returns:
        bool: false if the title implies Senior, Managerial, or lead, true otherwise
        """
        pattern = re.compile(r'[Ss]enior|[Mm]anager|[Ll]ead|[Ss]r|[Mm]ngr')
        isSeniorManagerialOrLead = pattern.search(title)
        return not isSeniorManagerialOrLead

    def qualificationsAreEntryLevel(self, qualifications):
        """
        Check if any of the qualifications indicate non entry level experience.

        Returns:
        bool: false if any of the qualifications indicate non entry level experience, true otherwise
        """
        qualifications_lower = [qualification.lower() for qualification in qualifications]

        # Fixed regex pattern with properly balanced parentheses
        years_pattern = re.compile(
            r'(?:(\d+)(?:\s*[-+]?\s*(?:years?|yrs?|y)|(?:[^\w\d]{1,5})(?:years?|yrs?|yr)))'
            r'|'
            r'(?:(one|two|three|four|five|six|seven|eight|nine|ten)(?:\+|&#43;)?\s*(?:&nbsp;|\s)*(?:year|yr)s?)'
        )

        # education and experience are not bachelors level if they mention graduate degrees without also including bachelor's degree"
        includesGrad = re.compile(r'(?:M\.S\.?|Ph\.?\s?D\.?|[Mm]aster([\\u0027]|\')?s|[Dd]octorate)')
            # MS is not included because it is a common abbreviation (microsoft) and common to end a sentance with.
        includesBachelors = re.compile(r'(BA|BS|Bachelor|BACHELOR)')

        for qualification in qualifications_lower:

            if years_pattern.search(qualification):
                return False
            if includesGrad.search(qualification) and not includesBachelors.search(qualification):
                return False
        return True

    def getEntryLevelPositionsFromList(self, allJobs : list[str], outputFilename="EntryLevelPositions.txt", writeTitle=True, printTimes=True, printResults=True) -> int:
        # TODO: since date parameter
        """
        Retrieves entry level job positions from a list of job URLs and writes them to a file.
        Also prints progress to the console.

        Returns:
        int the number of entry level positions found
        """
        t0 = time.time()



        # Update output path to use the outputs directory
        if not os.path.dirname(outputFilename):  # If no directory specified in filename
            output_path = os.path.join("job_outputs", outputFilename)
        else:
            output_path = outputFilename

        try:
            f = open(output_path, "a+")
            if(writeTitle):
                f.write(f"\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        except:
            print(f"failed to open file {output_path}")

        numEntryLevelPositions = 0
        for idx, job in enumerate(allJobs):
            jobPrintable = self.getJobPrintable(job)

            # Print progress every 20 jobs (there are  max 20 jobs per page)
            if (idx + 1 ) % 20 == 0:
                print(f"\nProcessed {idx+1} jobs. Time elapsed: {time.time() - t0}.")
                print(
                    f"Percent entry level: {numEntryLevelPositions / (idx+1) * 100}% (of {idx} jobs so far). "
                    f"Percent complete: {(idx+1) / len(allJobs) * 100}%. "
                    f"Expected time remaining: "
                    f"{(len(allJobs) - (idx+1)) / (idx + 1) * (time.time() - t0)/60} minutes\n"
                )
                f.flush()

            isEntryLevel = True

            # get the job description page
            jobData = self.getJobData(job)
            if jobData == None:
                continue

            # get the job title and check if it could be an entry level position
            # TODO: implement title getting/checking from search page
            # maybe just reges the url itself?
            title = ""
            try:
                title = self.getJobTitle(jobData)
            except:
                print(f"Could not get TITLE for {jobPrintable}")

            if not self.jobTitleIsEntryLevel(title):
                if printResults:
                    print(f"Job title {title} is not for an entry level position")
                isEntryLevel = False

            # get the qualifications and check if they could be for an entry level position
            qualifications = []
            try:
                qualifications = self.getQualifications(jobData)

            except:
                print(f"Could not get QUALIFICATIONS for {jobPrintable}")
            if not self.qualificationsAreEntryLevel(qualifications):
                if printResults:
                    print(f"Qualifications for {title} are not for an entry level position")
                isEntryLevel = False
            # write to file
            if isEntryLevel:
                if printResults:
                    print(f"Entry level position found: {jobPrintable}")
                f.write(f"{jobPrintable}\n")
                numEntryLevelPositions += 1

        t1 = time.time()
        if(printTimes):
            print(f"Time to get entry level positions: {t1-t0}")
        f.close()
        return numEntryLevelPositions

    def getEntryLevelPositions(self, onlyNew=False, isCached=False):
        raise NotImplementedError

    def getJobPrintable(self, job):
        raise NotImplementedError

class JobsScraperByApi(BaseJobsSiteScraper):
    def __init__(self):
        return None

    searchAPI = ""
    jobPageAPI = ""

