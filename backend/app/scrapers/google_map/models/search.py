from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class GoogleMapSearch(BaseModel):
    name: str
    type: Optional[str] = None
    address: Optional[str] = None
    rating: float
    reviews: int
    query: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    link: str
    image: Optional[str] = None

    @field_validator("rating", mode="before")
    @classmethod
    def clean_rating(cls, value):
        """Convert rating from string like '4.3' → float 4.3"""
        if value in (None, ""):
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    @field_validator("reviews", mode="before")
    @classmethod
    def clean_reviews(cls, value):
        """Extract digits from something like '1,234 reviews' → 1234"""
        if value in (None, ""):
            return 0
        if isinstance(value, str):
            digits = "".join(c for c in value if c.isdigit())
            return int(digits) if digits else 0
        return int(value)
