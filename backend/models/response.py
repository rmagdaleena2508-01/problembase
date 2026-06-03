from pydantic import BaseModel
from typing import List

class Complaint(BaseModel):
    text: str
    source: str
    url: str
    score: int

class ProblemCluster(BaseModel):
    theme: str
    severity: str
    complaint_count: int
    complaints: List[Complaint]
    insight: str

class SearchResponse(BaseModel):
    product: str
    total_complaints: int
    clusters: List[ProblemCluster]
    status: str
