import requests
from bs4 import BeautifulSoup
import time
import re

# meta Jobs URL
jobsURLPrefix = "https://www.metacareers.com/jobs"

# locationFilter = "location=united-states-USA"
locationFilter = "&offices[0]=Menlo%20Park%2C%20CA&offices[1]=Seattle%2C%20WA"
# locationFilter = "location=austin-metro-area-AUSMETRO+austin-AST"

# Apple Jobs URL with provided filters
jobsQueryURL = f"{jobsURLPrefix}?q=software{locationFilter}&sort_by_new=true"

# Suffix appended to jobsQueryURL to specify pagination
jobsQueryURLPageSuffix = "&page="

outputFilename = "MetaEntryLevelPositions.txt"

def getAllJobUrls(numPages, soup):
    """
    Retrieve all job URLs from the specified number of pages (all of them).

    Returns:
    list: A list of all the job URLs found for the query.
    """
    t0 = time.time()
    allJobUrls = []

    # Naive Pagination: loop from 1 to numPages (this should be the number of pages of job results)
    for pageIdx in range(1, numPages+1):
        # loop through all the pages
        currentJobResultsPage = jobsQueryURL + jobsQueryURLPageSuffix + str(pageIdx)

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

def getJobTitle(soup):
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

def TitleIsEntryLevel(title):
    """
    Check if the title could be for an entry level job.

    Returns:
    bool: false if the title implies Senior, Managerial, or lead, true otherwise
    """
    pattern = re.compile(r'[Ss]enior|[Mm]anager|[Ll]ead|[Ss]r|[Mm]ngr')
    isSeniorManagerialOrLead = pattern.search(title)
    return not isSeniorManagerialOrLead

def getQualifications(soup):
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
    keyQualificationsDiv = soup.find(id="jd-key-qualifications")
    assert keyQualificationsDiv != None, "No Key Qualifications Found based on standard format"
    keyQualificationsUl = keyQualificationsDiv.ul
    assert keyQualificationsUl != None, "Key Qualifications Does not contain ul"
    liQualifications = keyQualificationsUl.contents
    qualifications = [li.text for li in liQualifications]
    return qualifications

def qualificationsAreEntryLevel(qualifications):
    """
    Check if any of the qualifications indicate non entry level experience.
    
    Returns:
    bool: false if any of the qualifications indicate non entry level experience, true otherwise
    """
    # qualifications are not entry level they contain "n(+) years..."
    pattern = re.compile(r'\d+\+?\s(?:year|yr)')

    for qualification in qualifications:
        if pattern.search(qualification):
            return False
    return True

def getEdEx(soup):
    """
    Extracts the education and experience from the given soup object (job description page).
    Returns:
    String, the text content of the education and experience section
    """
    # the format of education and experience is as follows:
    # <div id="jd-education-experience">
    #   <span>education and experience</span>
    # </div>

    # extract the education and experience
    educationAndExperience = soup.find(id="jd-education-experience")
    assert educationAndExperience != None, "Education and Experience not found"
    assert len(educationAndExperience.contents) == 1, "Education and Experience have multiple parts"
    return educationAndExperience.text

def edExAreEntryLevel(educationAndExperience):
    """
    Determines if the education and experience are non entry level.
    Returns:
    bool: false if the education and experience are non entry level, true otherwise
    """
    
    # education and experience are not entry level if they contain "n(+) years of experience"
    pattern1 = re.compile(r'\d+\+?\s(?:year|yr)')
    # education and experience are not bachelors level if they mention graduate degrees without also including bachelor's degree"
    includesGrad = re.compile(r'(MS|PhD|Ph\.D\.|[Mm]aster|[Dd]octorate)')
    includesBachelors = re.compile(r'(BA|BS|Bachelor)')

    if pattern1.search(educationAndExperience):
        return False
    if includesGrad.search(educationAndExperience) and not includesBachelors.search(educationAndExperience):
        return False
    return True



if __name__ == "__main__":
    try:
        page = requests.get(jobsQueryURL)
        if "The page you’re looking for can’t be" in page.text:
            # TODO: regex for the "found"?
            print(f"Job URL {jobsQueryURL} could not be found")
            exit()
    except:
        print(f"Could not get page for {jobsQueryURL}")
        exit()
    soup = BeautifulSoup(page.content, "html.parser")
    
    # get all job URLs from website
    allJobUrls = getAllJobUrls(numPages, soup)
    # caching purposes (only about 0.1% change per hour)
    f = open("allJobUrlsCache.txt", "w")
    f.write(str(allJobUrls))
    f.close()

    # # get all job URLs from cached file
    # f = open("allJobUrlsCache.txt", "r")
    # allUrlsStr = f.read()
    # allJobUrls = list(eval(allUrlsStr))
    # print(f"Using the cached {len(allJobUrls)} urls")
    # f.close()

    # Testing Data
    # testTitlesUrls = ['/en-us/details/200525855/system-integration-lead?team=SFTWR','/en-us/details/200525606/software-engineering-program-manager-media-frameworks-apple-vision-pro?team=SFTWR','/en-us/details/200539431/senior-international-program-manager-services?team=SFTWR', '/en-us/details/200489593/natural-language-generative-modeling-research-engineer-siml-ise?team=MLAI', '/en-us/details/200519780/ai-safety-robustness-analysis-manager-system-intelligent-and-machine-learning-ise?team=SFTWR']
    # testQulificationsUrls = ["/en-us/details/200534209/database-engineer-employee-experience-productivity?team=SFTWR","/en-us/details/200539573/software-engineer-backup-migration?team=SFTWR", "/en-us/details/200538805/engineering-project-specialist-softgoods?team=HRDWR", "/en-us/details/200504957/wifi-embedded-software-engineer?team=SFTWR"]
    # getEntryLevelPositions(testTitlesUrls + testQulificationsUrls)

    print(f"Beginning to scan for entry level positions. This may take a while. Check {outputFilename} for results...")
    getEntryLevelPositions(allJobUrls)