from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class JobPosting:
  company: str
  title: str
  location: Optional[str] = None
  locations: Optional[List[str]] = None
  id: Optional[str] = None
  posting_url: Optional[str] = None
  posted_date: Optional[datetime] = None
  description: Optional[str] = None
  requirements: Optional[List[str]] = None
  salary_range: Optional[str] = None
  team: Optional[str] = None
  teams: Optional[List[str]] = None
  level: Optional[str] = None
  responsibilities: Optional[List[str]] = None
  extra_qualifications: Optional[List[str]] = None
