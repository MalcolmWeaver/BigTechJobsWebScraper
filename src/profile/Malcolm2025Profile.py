from .profile import DegreeType, Profile
from src.controller.ProfileCreator import ProfileCreator

resume_text = """
Malcolm Weaver



malcolm.weaver12128@gmail.com
425-241-8352
Github


Skills
Programming Languages: Elixir, Python, C++, C,, Kotlin, TypeScript, SQL
Web Technologies: React, Next.js, GraphQL, REST, HTTP
Tools: Git, Mix, Ecto, Google Cloud Platform (GCP), Google Tag Manager (GTM), Google Analytics (GA4)

Experiences

Full Stack Software Developer									            Winter 2024 - Present
Savvy
Built a vacation rental price comparison scraping tool, including APIs and frontend components to improve savings estimates by around 59% on savvy listings. I built a listing association algorithm to backfill airbnb and vrbo urls for 87% of listings and to automatically associated newly onboarded listings.
Automated flagging of broken booking URLs across all listings on savvy.com, and subsequent unpublishing of broken (unbookable) listings, successfully pruning over 3,000 broken listings.
Migrated savvy.com frontend from Emotion to Tailwind, simplifying styles and reducing dependencies (TypeScript, Next.js, Tailwind).

SDE Intern												         Summer 2023
Amazon (AWS Supply Chain Platform Team)
Created an API to translate and backfill customer identity management information into a hybrid RBAC/UBAC storage model.

SWE Intern												         Summer 2022
Meta (Storage Management Team)
Decreased loading times of debugging graphs by caching calculated values
Built Dataswarm (python and HiveQL) pipeline to refactor dependency scheduling of space/IO attribution agents (C++)

Projects

SCU Math Research
Santa Clara University								    		    February 2021 - June 2021
Developed and implemented an algorithm using Markov chains to calculate the expected value of achieving arbitrary strings of random events (coin-flips).
Initiated a group research project with 2 Professors and 1 other student to continue to investigate the mechanism behind expected value, which involved transition matrices, string searching algorithms, and enumeration of distinct probabilities.

Driven By Time
Inrix Hackathon												November 2021
Led the development of an application to read a user's google calendar events and create corresponding events specifying optimal departure time, based on driving, walking and parking time/availability. Won 3rd place overall.
API’s used: Google Geocoding, Google Calendar, Google Directions, and Inrix Parking

Education

Bachelor of Engineering Computer Science and Engineering,
Santa Clara University							            			 	            2020 - 2023
GPA: 3.8
Grader for Pre-calculus, Calculus and Analytical Geometry IV, Probability and Statistics

"""

brag_documents = """
Personal Projects
Sunroads Construction Website
Dec 2023  - Feb 2024
I rebuilt a business website using react, deployed with github pages and masked a domain from namecheap.

Big 5 Job Sites web scraper
Feb 2024
I built a web scraper using python to read jobs from job sites (or directly get publicly available apis) and return those that regex match with entry level descriptors. I implemented a base scraper class and children classes for Amazon, Apple, and Microsoft.
Nextjs kbb site.
Feb 2024
I built a nextjs website that emulates kbb to list car models using dynamically generated pages and routes as well as the ‘app’ structure. To hold car data, I used sqlite and then moved to vercel. To gather data, I scraped the kbb site rate limiting, and using selenium to handle client side rendering,

BNB Finder
Migrating bnbfinder frontend from emotion to tailwind
March 2024
I migrated bnbfinder.com website from emotion to tailwind. This improved simplicity and readability by defining styles solely through class names (using tailwind merge to explicitly define precedence). It allows us to remove frontend dependencies to avoid outdated libraries and reduce complexity. This allowed us to update next js to the app router.

Url Garbage Collector
April 2024 (and June 2024)
I created a task to go over every listing in our database and check the status of each url. We logged this information and also stored it into our database. Manual implementation for redirects of 303s. We then, with an ETL pipeline, ultimately reported this information to business intelligence. Technologies used: HTTPoison, heroku, postgres database
After talking with product, we decided that because of the stultifying user experience, we should unpublish listings that have broken book direct links. I implemented a task to automatically unpublish broken listings.
Admin field mapping encapsulation (April 2024)

In order to support account level customization, we stored data in our connection database. However, our architecture held the abstraction that all accounts could be interfaced with identically at every layer except for the specific integration layer. This, I abstracted out all of the logic involved in creating, getting and updating this information in the database, and stored it as a generic map to encapsulate it's entire implementation to an API in the proper layer.

Show More Properties Map Zoom Feature
Real Time Pricings (Streamline Partner, Owner Rez, Track, hostfully, hostaway, escapia, rentals united) (June 2024)
In order to implement pricing filters on bnbfinder web’s site, we needed to create adapters to ingest future pricing data from various property managers, into one length of stay array that we persist.

I implemented this for multiple different PMS APIs. This involved converting standard pricing to length of stay pricing and handling gaps in pricing calendars.
End To End Bookings (July 2024)
Implemented template string (handlebars) to link book direct urls to the appropriate page with date and guest number correctly copied
Ciirus Integration (August-November 2024)
Implemented the adapters and integration for bnbfinder with the Ciirus vacation rental software system. In addition to the basic functionality involved in showing Ciirus accounts and listings on bnbfinder.com, this enabled filtering by pricing, and the creation of end to end bookings directly from bnbfinder.com.
In this process, I discovered a number of bugs with CiiRus’ scheduling availability calculation, fees on native reservations, data synchronization standards, listing enablement, and documentation accuracy helping them fix these in the future while writing flexible software on our end to gather correct data out of both incorrect and correct API responses.
(How many listings were added as a result)
Availability/Pricing 2.0 Validation (July/August 2024)
Barefoot checkin/checkout rules

ETL Mail-list migration (January 2025)
Migrated mail list provider from mail chimp to Klaviyo, using Klaviyo APIs deployed on Google Cloud run.

Savvy.com
Quote Comparison Tool (December 2024)
Reverse engineered and deployed a web scraper to collect real time pricing information of competing online travel agencies. This demonstrated concretely that savvy.com saves over ten percent before taxes on almost all listings that are listed on Airbnb/Vrbo. The precises savings calculations formed and accuracy improvement of roughly 59%. I integrated this tool with the rest of the backend by building a rest API, and then to the frontend with a graphql api.
Designed a frontend UI component to display price comparisons to the same listing on different site in real time when a user looks at a quote on a listing to show savings accrued from savvy.com

Quote Comparison External URL Backfill (November/December 2024)
Designed and implemented an algorithm to use obfuscated location data and semantic description text to match listings from Savvy to external OTAs such as Airbnb and Vrbo.
Utilizing suffix trees running in O(n) to the the length of descriptions of the candidate listings, and perceptual image hash comparison.
Deploying this on proxies to backfill 112,000 listing, allowing for price comparison.

Quote Comparison Google Analytics (gtm, ga4)
Implemented analytics for price comparison tool using google tag manager and google analytics
Quote Comparison SRE
Implemented observability/monitoring for site reliability of SRE Comparison using domain and http level logging.
Auto Listing Association On Onboarding
I enhanced the Finder-Co Listing Engine by developing a feature to associate external OTA (Airbnb, Vrbo) listing URLs with internal listings, improving data synchronization and platform scalability through asynchronous job queuing, rigorous URL validation, and comprehensive error handling, while integrating observability enhancements from another microservice to improve logging and monitoring. Additionally, I implemented proxy rate limiting to manage API traffic efficiently and optimized Vrbo response sizes through pagination, achieving up to 63% savings in data transfer, enabling faster onboarding and enhancing system performance in high-density areas.
Price Comparison After Taxes Tool
I elevated the Finder-Co platform by developing a price comparison tool that displays accurate after-tax pricing for Airbnb and Vrbo listings, significantly increasing user trust by ensuring transparency throughout the booking process. This feature addresses user skepticism by proving that the final checkout price—where credit card details are entered—is genuinely competitive, as evidenced by comprehensive comparisons on the listing page, extending to both mobile and desktop views, and integrating efficient GraphQL queries, all while maintaining backwards compatibility for a seamless and confident user experience.
Portals Scraper

Technical Traffic
Implemented a scraper integration of Technical Traffic Consultants to assist with invoice processing automation, using purely http requests, building up cookies and authentication, submitting forms, and associating invoices by their probill ids.
WA Online
Implemented a scraper integration of WA Online Consultants to assist with invoice processing automation, using purely http requests, building up cookies and authentication, submitting forms, and associating invoices by their probill ids.

"""

class Malcolm2025Profile(ProfileCreator):
  def create_profile(self):

    return Profile(years_of_experience=2, degree=DegreeType.BACHELORS, resume_text=resume_text, brag_documents=brag_documents)
