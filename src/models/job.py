from dataclasses import dataclass
from datetime import datetime
# from typing import Optional, List
# from datetime import datetime

@dataclass
class JobPosting:
  company: str
  title: str
  id: str = ""
  posting_url: str = ""
  description: str = ""
  responsibilities: str = ""
  all_qualifications: str = ""
  is_match: bool = False
  match_reason: str = ""
  generated_cv: str = ""
  scraped_at: datetime | None = None
  location: str = ""

  # team: Optional[str] = None
  # teams: Optional[List[str]] = None
  # posted_date: Optional[datetime] = None
  # location: Optional[str] = None
  # locations: Optional[List[str]] = None