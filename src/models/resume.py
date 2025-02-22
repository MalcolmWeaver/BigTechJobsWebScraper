class Resume:
  resume_text: str = ""

  def __init__(self):
    self.resume_text = """
Malcolm Weaver



malcolm.weaver12128@gmail.com
425-241-8352
Github


Skills
Programming Languages: Elixir, Python, C++, C,, Kotlin, TypeScript
Web Technologies: React, Next.js, GraphQL, REST, HTTP, TCP
Databases: SQL
Cloud Technologies: Google Cloud Platform (GCP)
Tools: Git, Mix, Ecto
Other: Data Analysis, Problem-Solving, Automation, Software Engineering, API Development

Experiences

Full Stack Software Developer									            Winter 2024 - Present
Savvy
Developed a price comparison tool, deploying web scrapers, designing RESTful and GraphQL APIs, and implementing frontend changes in React and Next.js. This improved customer savings estimates by 59% by comparing prices between savvy.com and competitor OTAs. Leveraged Google Cloud Run for deployment. Addressed challenging site reliability engineering (SRE) issues, including implementing strategies to mitigate aggressive bot attacks and maintain scraper functionality.
Led the integration of Ciirus vacation rental software, enabling end-to-end booking functionality and pricing filter implementation.
Automated the identification and removal of over 3,000 broken (unbookable) listings on savvy.com by developing a system to flag broken booking URLs. This involved Elixir, Ecto, and HTTPoison.
Migrated the savvy.com frontend from Emotion to Tailwind CSS, simplifying styles, reducing dependencies, and improving maintainability. Utilized TypeScript and Next.js, and employed tailwind-merge for efficient style combination.

SDE Intern												         Summer 2023
Amazon (AWS Supply Chain Platform Team)
Designed and implemented an API to translate and backfill customer identity management data into a more efficient storage model, validating results to ensure data integrity.

SWE Intern												         Summer 2022
Meta (Storage Management Team)
Improved the performance of debugging graphs by implementing a caching mechanism, resulting in a measurable reduction in loading times.
Developed "Dataswarm," a Python and HiveQL ETL pipeline, to replace and enhance the dependency scheduling of C++ attribution agents. These agents collect space usage data across various storage platforms at Meta. Implemented data quality checks to ensure data consistency.

Projects

SCU Math Research
Santa Clara University								    		    February 2021 - June 2021
Developed and Implemented an algorithm using Markov chains to calculate the expected value of achieving arbitrary strings of random events (coin-flips).
Initiated a group research project with 2 Professors and 1 other student to continue to investigate the mechanism behind expected value, which involved transition matrices, string searching algorithms, and enumeration of distinct probabilities.
Driven By Time
Inrix Hackathon												November 2021
Led the development of an application to read a user's google calendar events and create corresponding events specifying optimal departure time, based on driving, walking and parking time/availability. Won 3rd place overall.
Technologies used: Python and Github
API’s used: Google Geocoding, Google Calendar, Google Directions, and Inrix Parking

Education

Bachelor of Engineering Computer Science and Engineering,
Santa Clara University							            			 	            2020 - 2023
GPA: 3.8
Grader for Pre-calculus, Calculus and Analytical Geometry IV, Probability and Statistics

"""