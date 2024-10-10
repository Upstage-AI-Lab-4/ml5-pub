from pydantic import BaseModel
from typing import List

class RecommendationItem(BaseModel):
    track_name: str
    track_artist: str
    release_year: int
    final_score: float
    
class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]