import requests
from bs4 import BeautifulSoup
import time
from utils import BaseJobsSiteScraper

class Apple(BaseJobsSiteScraper):

    def __init__(self, location="Seattle"):
        super().__init__(location)
        self.location = location
        self.jobsQueryURL = self.getQueryURL(location)
        self.jobsQueryURL = (
            f"{self.jobsURLPrefix}/en-us/search?"
            f"{self.locations[self.location]}"
            f"{self.sortSeg}"
            "&team=devops-and-site-reliability-SFTWR-DSR%20"
            "engineering-project-management-SFTWR-EPM%20"
            "information-systems-and-technology-SFTWR-ISTECH%20"
            "machine-learning-and-ai-SFTWR-MCHLN%20security-and-"
            "privacy-SFTWR-SEC%20software-quality-automation-and-tools-SFTWR-SQAT%20"
            "wireless-software-SFTWR-WSFT%20analog-and-digital-design-HRDWR-ADD%20"
            "engineering-project-management-HRDWR-EPM%20machine-learning-and-"
            "ai-HRDWR-MCHLN%20system-design-and-test-engineering-HRDWR-SDE%20"
            "wireless-hardware-HRDWR-WT%20machine-learning-infrastructure-MLAI-MLI%20"
            "deep-learning-and-reinforcement-learning-MLAI-DLRL%20"
            "natural-language-processing-and-speech-technologies-MLAI-NLP%20"
            "computer-vision-MLAI-CV%20cloud-and-infrastructure-SFTWR-CLD%20"
            "apps-and-frameworks-SFTWR-AF%20core-operating-systems-SFTWR-COS&"
        )
    # Apple Jobs URL
    jobsURLPrefix = "https://jobs.apple.com"

    locations = {
        "Seattle": "location=washington-state1000",
        "Austin": "location=austin-metro-area-AUSMETRO+austin-AST",
        "Bay Area": "location=san-francisco-bay-area-SFMETRO",
    }

    sortSeg = "&sort_by=new"


    # Apple Jobs URL with provided filters
    def getQueryURL(self, location):
        return f"{self.jobsURLPrefix}/en-us/search?{self.locations[self.location]}{self.sortSeg}&&team=devops-and-site-reliability-SFTWR-DSR%20engineering-project-management-SFTWR-EPM%20information-systems-and-technology-SFTWR-ISTECH%20machine-learning-and-ai-SFTWR-MCHLN%20security-and-privacy-SFTWR-SEC%20software-quality-automation-and-tools-SFTWR-SQAT%20wireless-software-SFTWR-WSFT%20analog-and-digital-design-HRDWR-ADD%20engineering-project-management-HRDWR-EPM%20machine-learning-and-ai-HRDWR-MCHLN%20system-design-and-test-engineering-HRDWR-SDE%20wireless-hardware-HRDWR-WT%20machine-learning-infrastructure-MLAI-MLI%20deep-learning-and-reinforcement-learning-MLAI-DLRL%20natural-language-processing-and-speech-technologies-MLAI-NLP%20computer-vision-MLAI-CV%20cloud-and-infrastructure-SFTWR-CLD%20apps-and-frameworks-SFTWR-AF%20core-operating-systems-SFTWR-COS&"

    # Suffix appended to jobsQueryURL to specify pagination
    jobsQueryURLPageSuffix = "&page="

    def getJobPrintable(self, job):
        return f"https://jobs.apple.com{job}"

    def getJobUrl(self, job):
        return f"{self.jobsURLPrefix}{job}"

    def getAllJobUrls(self, soup, onlyNew=False, last5Jobs=[]):
        """
        Retrieve all job URLs from the specified number of pages (all of them).

        Returns:
        list: A list of all the job URLs found for the query.
        """
        t0 = time.time()
        allJobUrls = []
        numPages = getNumberOfPages(soup)
        """Only New Logic: save the most recent 5 jobs. If you one of those jobs (sorted by newest), you're done.
        This logic breaks down when all 5 of the most recent jobs are deleted, but by then, you should probably rerun everything
        """

        # Naive Pagination: loop from 1 to numPages (this should be the number of pages of job results)
        for pageIdx in range(1, numPages+1):
            # loop through all the pages
            currentJobResultsPage = self.jobsQueryURL + self.jobsQueryURLPageSuffix + str(pageIdx)

            try:
                page = requests.get(currentJobResultsPage)
            except:
                print(f"Could not get page for {currentJobResultsPage}")
                continue
            #TODO: test page number too high

            soup = BeautifulSoup(page.content, "html.parser")

            # Pagination checking
            pageNumber = getCurrentPageNumber(soup)
            assert pageNumber == pageIdx, "Page number does not match pagination index"

            newJobUrlsFromQuery = getJobUrlsFromJobsQueriedPage(soup)
            if onlyNew:
                for idx, job in enumerate(newJobUrlsFromQuery):
                    if job in last5Jobs:
                        allJobUrls += newJobUrlsFromQuery[:idx]
                        return allJobUrls


            allJobUrls += newJobUrlsFromQuery

        t1 = time.time()
        print(f"Total number of Apple jobs found: {len(allJobUrls)}. Elapsed time: {t1-t0}")
        return allJobUrls



    def getJobTitle(self, soup):
        """
        Get the job title from the provided soup object (job description page).

        Returns:
        The job title extracted from the soup object.
        """

        # Find the element with id "jdPostingTitle"
        jd_title = soup.find(id="jdPostingTitle")

        # Ensure that the title element is found
        assert jd_title is not None, "No Title Found based on standard format"

        # Return the text of the title element
        return jd_title.text

    def getQualifications(self, soup):
        """
        Extracts the qualifications from the given soup object (job description page).

        Returns:
        List of strings, the qualifications (bullet points) extracted from the soup object.
        """
        # The html format of key qualifications is as follows:
        # <div id="jd-key-qualifications">
        #   <ul>
        #     <li>qualification bullet point</li>
        #     <li>qualification bullet point</li>
        #     ...
        #   </ul>
        # </div>

        # extract the qualifications
        allReqs = []

        qualifications = []
        keyQualificationsDiv = soup.find(id="jd-key-qualifications")
        if keyQualificationsDiv != None:
            keyQualificationsUl = keyQualificationsDiv.ul
            assert keyQualificationsUl != None, "Key Qualifications Does not contain ul"
            liQualifications = keyQualificationsUl.contents
            qualifications = [li.text for li in liQualifications]

        # print("qualifications are: ", qualifications)

        # the format of additional requirements is as follows:

        # <div id="jd-additional-requirements">
        #   <ul>
        #     <li>additional requirement bullet point</li>
        #     <li>additional requirement bullet point</li>
        #     ...
        #   </ul>
        # </div>

        # extract min requirements
        minReqs = []
        minRequirements = soup.find(id="jd-minimum-qualifications")
        if minRequirements != None:
            minReqsUl = minRequirements.ul
            assert minReqsUl != None, "Key Qualifications Does not contain ul"
            liMinReqs = minReqsUl.contents
            minReqs = [li.text for li in liMinReqs]

        # extract the additional requirements
        addReqs = []
        additionalRequirements = soup.find(id="jd-additional-requirements")
        if additionalRequirements != None:
            addReqsUl = additionalRequirements.ul
            assert addReqsUl != None, "Key Qualifications Does not contain ul"
            liAddReqs = addReqsUl.contents
            addReqs = [li.text for li in liAddReqs]

        # print("addReqs are: ", addReqs)

        # the format of education and experience is as follows:

        # <div id="jd-education-experience">
        #   <span>education and experience</span>
        # </div>

        # extract the education and experience
        educationAndExperienceText = ""
        educationAndExperience = soup.find(id="jd-education-experience")
        if(educationAndExperience):
            if(educationAndExperience.span != None):
                educationAndExperienceText = educationAndExperience.span.text

        # print("educationAndExperienceText is: ", educationAndExperienceText)

        descriptionText = ""
        description = soup.find(id="jd-description")
        if(description):
            if(description.span != None):
                descriptionText = description.span.text

        # print("descriptionText is: ", descriptionText)

        allReqs.append(educationAndExperienceText)
        allReqs.append(descriptionText)
        allReqs += qualifications
        allReqs += addReqs
        allReqs += minReqs

        return allReqs

    def getJobData(self, job):
        jobUrl = self.getJobUrl(job)
        print("Job URL:", jobUrl)
        try:
            page = requests.get(jobUrl)
            if "The page you’re looking for can’t be" in page.text or "404 Not Found" in page.text:
                print(f"Job URL {jobUrl} could not be found")
                isEntryLevel = False
        except:
            print(f"Could not get page for {jobUrl}")
            return None
        return BeautifulSoup(page.content, "html.parser")

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
            assert not isCached, "Cached data is not new data. Make sure if you select onlyNew, isCached is False."

        try:
            page = requests.get(self.jobsQueryURL)
            if "The page you’re looking for can’t be" in page.text:
                print(f"Job URL {self.jobsQueryURL} could not be found")
                exit()
        except:
            print(f"Could not get page for {self.jobsQueryURL}")
            exit()
        soup = BeautifulSoup(page.content, "html.parser")

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
                newJobUrls = self.getAllJobUrls(soup, onlyNew=onlyNew, last5Jobs=allJobUrls[:5])
                if newJobUrls == []:
                    print("No new jobs found")
                    return
                allJobUrls = newJobUrls
            else :
                # get number of pages for naive iteration
                allJobUrls = self.getAllJobUrls(soup, onlyNew=onlyNew)
            f = open(self.jobTitlesCacheFilename, "w")
            f.write(str(allJobUrls)+"\n")
            print(f"{len(allJobUrls)} urls were cached from {self.jobsQueryURL}")
            f.close()

        print(f"Beginning to scan for entry level positions. This may take a while. Check {self.outputFilename} for results...")
        self.getEntryLevelPositionsFromList(allJobUrls, self.outputFilename)



def getNumberOfPages(soup):
    """
    Funtion to get number of pages to loop through for naive pagination by reading html (see element with id="frmPagination")

    Returns: (int) the number of pages of the job query results according to the website
    """
    pageNumberElements = soup.find_all(class_="pageNumber")
    assert len(pageNumberElements) == 2, "Page Numbers (id='frmPagination') Formatting Has Changed"
    numPages = int(pageNumberElements[1].text)
    return numPages

# Apple specific functions
def getCurrentPageNumber(soup):
    pageNumber = soup.find(id="page-number")
    return(int(pageNumber.attrs['value']))

def getJobUrlsFromJobsQueriedPage(soup):
    """
    Function to get job URLs from the job queried page's soup.

    Returns:
    list: A list of job URLs extracted from the soup of a (one of many) page.
    """

    # find all job titles from the queried table
    jobElements = soup.find_all(class_="table--advanced-search__title")
    assert len(jobElements) > 0, "No Jobs Found"

    # get the link to each job posting from the job query
    jobUrls = [jobElement["href"] for jobElement in jobElements]
    return jobUrls

if __name__ == "__main__":
    location = input("Enter location (Seattle, Austin, Bay Area): ")
    if location not in ["Seattle", "Austin", "Bay Area"]:
        print("Invalid location. Please enter a valid location.")
        exit()
    apple = Apple(location=location)
    onlyNew = False
    apple.getEntryLevelPositions(onlyNew=True, isCached=False)

 # Testing Data
# testTitlesUrls = ['/en-us/details/200525855/system-integration-lead?team=SFTWR','/en-us/details/200525606/software-engineering-program-manager-media-frameworks-apple-vision-pro?team=SFTWR','/en-us/details/200539431/senior-international-program-manager-services?team=SFTWR', '/en-us/details/200489593/natural-language-generative-modeling-research-engineer-siml-ise?team=MLAI', '/en-us/details/200519780/ai-safety-robustness-analysis-manager-system-intelligent-and-machine-learning-ise?team=SFTWR']
# testQulificationsUrls = ["/en-us/details/200534209/database-engineer-employee-experience-productivity?team=SFTWR","/en-us/details/200539573/software-engineer-backup-migration?team=SFTWR", "/en-us/details/200538805/engineering-project-specialist-softgoods?team=HRDWR", "/en-us/details/200504957/wifi-embedded-software-engineer?team=SFTWR"]
# getEntryLevelPositions(testTitlesUrls + testQulificationsUrls)