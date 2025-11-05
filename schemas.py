"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Campaign -> "campaign" collection
- Donation -> "donation" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

# Example user schema (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

# Fundraising platform schemas

CATEGORIES: List[str] = [
    "Medical",
    "Education",
    "NGOs",
    "Environment",
    "Animal Care",
    "Disaster Relief",
    "Personal Causes",
]

class Campaign(BaseModel):
    title: str = Field(..., description="Campaign title")
    description: Optional[str] = Field(None, description="Campaign description")
    goal: float = Field(..., ge=1, description="Fundraising goal amount")
    raised: float = Field(0, ge=0, description="Amount raised so far")
    category: str = Field(..., description="Campaign category")
    image_url: Optional[HttpUrl] = Field(None, description="Hero image URL")
    organizer_name: Optional[str] = Field(None, description="Organizer's name")
    is_trending: bool = Field(False, description="Flag to mark as trending")

class Donation(BaseModel):
    campaign_id: str = Field(..., description="Associated campaign _id as string")
    donor_name: Optional[str] = Field(None, description="Donor name")
    amount: float = Field(..., ge=1, description="Donation amount")
    message: Optional[str] = Field(None, description="Support message")
    payment_status: str = Field("succeeded", description="Payment status placeholder")
    donated_at: Optional[datetime] = Field(default=None, description="Donation timestamp")
