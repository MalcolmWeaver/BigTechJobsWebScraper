import requests
from bs4 import BeautifulSoup
import time
from utils import BaseJobsSiteScraper

class Meta(BaseJobsSiteScraper):

    def __init__(self, location="ALLLOCATIONS"):
        super().__init__(location)
        self.location = location
        self.jobsQueryURL = self.getQueryURL(location)
    # Apple Jobs URL
    jobsURLPrefix = "https://www.metacareers.com/jobs/"


    # Apple Jobs URL with provided filters
    def getQueryURL(self, _location):
        return f"https://www.metacareers.com/jobs/?is_leadership=0&is_in_page=0&teams[0]=Software%20Engineering&offices[0]=Bellevue%2C%20WA&offices[1]=Redmond%2C%20WA&offices[2]=Santa%20Clara%2C%20CA&offices[3]=Menlo%20Park%2C%20CA&offices[4]=Sunnyvale%2C%20CA&offices[5]=Austin%2C%20TX&offices[6]=Seattle%2C%20WA&offices[7]=Fremont%2C%20CA"

    # Suffix appended to jobsQueryURL to specify pagination
    jobsQueryURLPageSuffix = "&page="

    def getJobPrintable(self, job):
        return f"{self.jobsURLPrefix}{job}"

    def getJobUrl(self, job):
        return f"{self.jobsURLPrefix}{job}"


    def getJobTitle(self, soup):
        """
        Get the job title from the provided soup object (job description page).

        Returns:
        The job title extracted from the soup object.
        """

      #  TODO

    def getQualifications(self, soup):
        """
        Extracts the qualifications from the given soup object (job description page).

        Returns:
        List of strings, the qualifications (bullet points) extracted from the soup object.
        """
        # TODO

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

    def getAllJobs(self, pageNumber, onlyNew=False, last5Jobs=[]):
      try:

        url = 'https://www.metacareers.com/graphql'
        headers = {
            'cookie': 'datr=kqwvZ8AxrhTIDC9cuBWxeJVw; ps_l=1; ps_n=1; cp_sess=FvT8yMq8qS4WNBgOMzZjQUFEeFV6WjJ5a1EW7Mif%2BAwA; wd=1279x999',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'fb_dtsg': 'NAcNiFJwddWAvbKEak5n4KwgIebZSHuY6Sc7RmQ7AcBXI3b52imRlVg:26:1736700470',
            'variables': '{"search_input":{"q":null,"divisions":[],"offices":["Bellevue, WA","Redmond, WA","Santa Clara, CA","Menlo Park, CA","Sunnyvale, CA","Austin, TX","Seattle, WA","Fremont, CA"],"roles":[],"leadership_levels":[],"saved_jobs":[],"saved_searches":[],"sub_teams":[],"teams":["Software Engineering"],"is_leadership":false,"is_remote_only":false,"sort_by_new":false,"results_per_page":null}}',
            'doc_id': '9114524511922157'
        }

        response = requests.post(url, headers=headers, data=data)
        return response.json()
      except:
        print(f"Could not get page for {url}")
        return None

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
            jobs = self.getAllJobs(1, onlyNew=onlyNew)
            jobs_objs = jobs['data']['job_search']
        except:
            print(f"Could not get page for {self.jobsQueryURL}")
            exit()

        allJobUrls = [self.getJobUrl(job['id']) for job in jobs_objs]
        print(allJobUrls)

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
    meta = Meta()
    onlyNew = False
    meta.getEntryLevelPositions(onlyNew=False, isCached=False)

 # Testing Data
# testTitlesUrls = ['/en-us/details/200525855/system-integration-lead?team=SFTWR','/en-us/details/200525606/software-engineering-program-manager-media-frameworks-apple-vision-pro?team=SFTWR','/en-us/details/200539431/senior-international-program-manager-services?team=SFTWR', '/en-us/details/200489593/natural-language-generative-modeling-research-engineer-siml-ise?team=MLAI', '/en-us/details/200519780/ai-safety-robustness-analysis-manager-system-intelligent-and-machine-learning-ise?team=SFTWR']
# testQulificationsUrls = ["/en-us/details/200534209/database-engineer-employee-experience-productivity?team=SFTWR","/en-us/details/200539573/software-engineer-backup-migration?team=SFTWR", "/en-us/details/200538805/engineering-project-specialist-softgoods?team=HRDWR", "/en-us/details/200504957/wifi-embedded-software-engineer?team=SFTWR"]
# getEntryLevelPositions(testTitlesUrls + testQulificationsUrls)