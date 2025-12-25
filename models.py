from dataclasses import dataclass
from typing import Optional


@dataclass
class Grade:
    student_no: str
    name: str
    subject: str
    score: float
    id: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class GradeFilters:
    student_no: str = ""
    name: str = ""
    subject: str = ""
