from .profile import DegreeType, Profile
from src.controller.ProfileCreator import ProfileCreator

class Malcolm2025Profile(ProfileCreator):
  def create_profile(self):
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
    return Profile(years_of_experience=2, degree=DegreeType.BACHELORS, resume_text=resume_text)
