from enum import Enum

class DegreeType(Enum):
    NONE = "None"
    HIGH_SCHOOL = "High School"
    ASSOCIATES = "Associates"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PhD"

class Profile:
  def __init__(self, years_of_experience: int, degree: DegreeType, resume_text: str, brag_documents: str):
    self.resume_text = resume_text
    self.years_of_experience = years_of_experience
    self.degree = degree
    self.brag_documents = brag_documents