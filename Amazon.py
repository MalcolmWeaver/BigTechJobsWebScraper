import requests
from bs4 import BeautifulSoup
import time
import re
from utils import BaseJobsSiteScraper

class Amazon(BaseJobsSiteScraper):
    def __init__(self):
        print("Meta Jobs Scraper")
        print("Base Query URL:", self.jobsQueryURL)

    # Meta Careers URL
    jobsURLPrefix = "https://www.metacareers.com/jobs/"

    locationFilter = "&offices[0]=Menlo%20Park%2C%20CA&offices[1]=Austin%2C%20TX&offices"

    # Apple Jobs URL with provided filters
    jobsQueryURL = f"{jobsURLPrefix}/?q=software&sort_by_new=true{locationFilter}"

    outputFilename = "EntryLevelPositionsAppleFebMeta.txt"

    def getAllJobUrls(self, soup):
        return super().getAllJobUrls(soup)
    
    def getJobUrl(self) -> str:
        return super().getJobUrl()
    
    def getJobTitle(self, soup) -> str:
        return super().getJobTitle(soup)
    
    def getQualifications(self, soup) -> list[str]:
        return super().getQualifications(soup)
    


if __name__ == "__main__":
    