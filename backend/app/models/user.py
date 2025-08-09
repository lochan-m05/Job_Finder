from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from passlib.context import CryptContext
from enum import Enum

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class SearchPreferences(BaseModel):
    preferred_locations: List[str] = []
    preferred_job_types: List[str] = []
    preferred_experience_levels: List[str] = []
    salary_range_min: Optional[float] = None
    salary_range_max: Optional[float] = None
    skills: List[str] = []
    exclude_companies: List[str] = []

class NotificationSettings(BaseModel):
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    job_alerts: bool = True
    newsletter: bool = False

class UserModel(Document):
    # Basic user information
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    full_name: str
    hashed_password: str
    
    # Profile information
    phone: Optional[str] = None
    location: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_profile: Optional[str] = None
    
    # User role and permissions
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    
    # Preferences
    search_preferences: SearchPreferences = SearchPreferences()
    notification_settings: NotificationSettings = NotificationSettings()
    
    # Usage tracking
    search_count: int = 0
    daily_search_limit: int = 100
    last_search: Optional[datetime] = None
    
    # Saved items
    saved_jobs: List[str] = []  # Job IDs
    saved_contacts: List[str] = []  # Contact IDs
    saved_searches: List[dict] = []
    
    # Account metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    subscription_expires: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "role",
            "is_active",
            "created_at"
        ]
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify a password against the hash"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def set_password(self, password: str):
        """Set user password"""
        self.hashed_password = self.get_password_hash(password)

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    phone: Optional[str] = None
    location: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_profile: Optional[str] = None
    search_preferences: Optional[SearchPreferences] = None
    notification_settings: Optional[NotificationSettings] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    search_count: int
    subscription_expires: Optional[datetime]

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    
class TokenData(BaseModel):
    email: Optional[str] = None
