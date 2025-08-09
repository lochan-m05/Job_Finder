from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ContactType(str, Enum):
    RECRUITER = "recruiter"
    HR = "hr"
    HIRING_MANAGER = "hiring_manager"
    COMPANY_CONTACT = "company_contact"

class ContactSource(str, Enum):
    LINKEDIN = "linkedin"
    COMPANY_WEBSITE = "company_website"
    JOB_POSTING = "job_posting"
    SOCIAL_MEDIA = "social_media"
    EMAIL_EXTRACTION = "email_extraction"

class SocialProfileModel(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None

class PhoneModel(BaseModel):
    number: str
    country_code: Optional[str] = None
    is_whatsapp: bool = False
    is_verified: bool = False

class EmailModel(BaseModel):
    email: EmailStr
    is_verified: bool = False
    is_primary: bool = True
    domain: Optional[str] = None

class ContactModel(Document):
    # Basic information
    name: Indexed(str)
    title: Optional[str] = None
    company: Indexed(str)
    
    # Contact details
    emails: List[EmailModel] = []
    phones: List[PhoneModel] = []
    social_profiles: SocialProfileModel = SocialProfileModel()
    
    # Contact metadata
    contact_type: ContactType
    source: ContactSource
    extracted_from_url: Optional[str] = None
    
    # Verification and quality
    email_verification_status: str = "pending"  # pending, verified, failed
    phone_verification_status: str = "pending"
    reliability_score: Optional[float] = None
    
    # Associated jobs and companies
    associated_job_ids: List[str] = []
    department: Optional[str] = None
    
    # Extraction metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    last_verified: Optional[datetime] = None
    extraction_confidence: Optional[float] = None
    
    # Activity tracking
    contact_attempts: int = 0
    last_contacted: Optional[datetime] = None
    response_received: bool = False
    
    # Additional info
    notes: Optional[str] = None
    tags: List[str] = []
    is_active: bool = True
    
    class Settings:
        name = "contacts"
        indexes = [
            "name",
            "company",
            "emails.email",
            "contact_type",
            "source",
            "extracted_at",
            "is_active"
        ]

class ContactExtraction(BaseModel):
    """Model for contact extraction requests"""
    url: str
    contact_types: List[ContactType] = [ContactType.RECRUITER, ContactType.HR]
    extract_emails: bool = True
    extract_phones: bool = True
    extract_social: bool = True
    
class ContactSearchRequest(BaseModel):
    """Model for searching contacts"""
    company: Optional[str] = None
    name: Optional[str] = None
    contact_type: Optional[ContactType] = None
    email_domain: Optional[str] = None
    has_phone: Optional[bool] = None
    has_whatsapp: Optional[bool] = None
    verified_only: bool = False
    
class ContactResponse(BaseModel):
    """Response model for contact information"""
    id: str
    name: str
    title: Optional[str]
    company: str
    emails: List[EmailModel]
    phones: List[PhoneModel]
    social_profiles: SocialProfileModel
    contact_type: ContactType
    reliability_score: Optional[float]
    last_verified: Optional[datetime]
