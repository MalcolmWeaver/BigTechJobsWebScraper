import requests
from bs4 import BeautifulSoup
import time
import re
from utils import NewJobsSiteScraper, BaseJobsSiteScraper

class Apple(BaseJobsSiteScraper):
    
    def __init__(self):
        print("Apple Jobs Scraper")
        print("Base Query URL:", self.jobsQueryURL)

    

    jobTitlesCacheFilename = "allJobUrlsCacheTest.txt"

    # Apple Jobs URL
    jobsURLPrefix = "https://jobs.apple.com"

    # locationFilter = "location=united-states-USA"
    locationFilter = "location=washington-state1000"
    # locationFilter = "location=austin-metro-area-AUSMETRO+austin-AST"

    sortSeg = "&sort_by=new"

    # Apple Jobs URL with provided filters
    jobsQueryURL = f"{jobsURLPrefix}/en-us/search?{locationFilter}{sortSeg}&&team=devops-and-site-reliability-SFTWR-DSR%20engineering-project-management-SFTWR-EPM%20information-systems-and-technology-SFTWR-ISTECH%20machine-learning-and-ai-SFTWR-MCHLN%20security-and-privacy-SFTWR-SEC%20software-quality-automation-and-tools-SFTWR-SQAT%20wireless-software-SFTWR-WSFT%20analog-and-digital-design-HRDWR-ADD%20engineering-project-management-HRDWR-EPM%20machine-learning-and-ai-HRDWR-MCHLN%20system-design-and-test-engineering-HRDWR-SDE%20wireless-hardware-HRDWR-WT%20machine-learning-infrastructure-MLAI-MLI%20deep-learning-and-reinforcement-learning-MLAI-DLRL%20natural-language-processing-and-speech-technologies-MLAI-NLP%20computer-vision-MLAI-CV%20cloud-and-infrastructure-SFTWR-CLD%20apps-and-frameworks-SFTWR-AF%20core-operating-systems-SFTWR-COS&"

    # Suffix appended to jobsQueryURL to specify pagination
    jobsQueryURLPageSuffix = "&page="

    outputFilename = "no-output-filename"
    def getOutputFilename(self):
        outputFilename = f"{self.__class__.__name__}EntryLevelPositions-{self.jobsQueryURL}.txt"
    

    def getJobUrl(self, job):
        return f"{self.jobsURLPrefix}{job}"
    
    def getAllJobUrls(self, soup):
        """
        Retrieve all job URLs from the specified number of pages (all of them).

        Returns:
        list: A list of all the job URLs found for the query.
        """
        t0 = time.time()
        allJobUrls = []

        numPages = getNumberOfPages(soup)
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

            allJobUrls += getJobUrlsFromJobsQueriedPage(soup)

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

        return allReqs


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
    apple = Apple()
    useCache = True
    apple.getEntryLevelPositions(useCache)

 # Testing Data
# testTitlesUrls = ['/en-us/details/200525855/system-integration-lead?team=SFTWR','/en-us/details/200525606/software-engineering-program-manager-media-frameworks-apple-vision-pro?team=SFTWR','/en-us/details/200539431/senior-international-program-manager-services?team=SFTWR', '/en-us/details/200489593/natural-language-generative-modeling-research-engineer-siml-ise?team=MLAI', '/en-us/details/200519780/ai-safety-robustness-analysis-manager-system-intelligent-and-machine-learning-ise?team=SFTWR']
# testQulificationsUrls = ["/en-us/details/200534209/database-engineer-employee-experience-productivity?team=SFTWR","/en-us/details/200539573/software-engineer-backup-migration?team=SFTWR", "/en-us/details/200538805/engineering-project-specialist-softgoods?team=HRDWR", "/en-us/details/200504957/wifi-embedded-software-engineer?team=SFTWR"]
# getEntryLevelPositions(testTitlesUrls + testQulificationsUrls)