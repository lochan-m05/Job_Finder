from beanie import Document, Indexed
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    JOB_SCRAPING = "job_scraping"
    CONTACT_EXTRACTION = "contact_extraction"
    NLP_ANALYSIS = "nlp_analysis"
    DATA_CLEANUP = "data_cleanup"

class ScrapingTaskModel(Document):
    # Task identification
    task_id: Indexed(str, unique=True)
    task_type: TaskType
    user_id: Optional[str] = None
    
    # Task parameters
    hashtags: List[str] = []
    sources: List[str] = []
    time_filter: str = "24h"
    additional_params: Dict[str, Any] = {}
    
    # Task status and timing
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and progress
    total_items_to_process: Optional[int] = None
    items_processed: int = 0
    items_succeeded: int = 0
    items_failed: int = 0
    
    # Result data
    result_job_ids: List[str] = []
    result_contact_ids: List[str] = []
    result_summary: Dict[str, Any] = {}
    
    # Error handling
    error_message: Optional[str] = None
    error_details: Dict[str, Any] = {}
    retry_count: int = 0
    max_retries: int = 3
    
    # Performance metrics
    execution_time_seconds: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    
    class Settings:
        name = "scraping_tasks"
        indexes = [
            "task_id",
            "task_type",
            "user_id",
            "status",
            "created_at",
            "hashtags"
        ]

class TaskRequest(BaseModel):
    """Model for creating new scraping tasks"""
    task_type: TaskType
    hashtags: List[str] = []
    sources: List[str] = ["linkedin", "naukri", "indeed"]
    time_filter: str = "24h"
    additional_params: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    """Response model for task information"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    created_at: datetime
    progress_percentage: float
    items_processed: int
    items_succeeded: int
    items_failed: int
    result_summary: Dict[str, Any]
    error_message: Optional[str]

class TaskProgress(BaseModel):
    """Model for task progress updates"""
    task_id: str
    status: TaskStatus
    items_processed: int
    items_succeeded: int
    items_failed: int
    current_operation: Optional[str] = None
    estimated_completion: Optional[datetime] = None
