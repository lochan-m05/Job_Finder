from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery instance
celery_app = Celery(
    "job_discovery",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "app.tasks.scraping_tasks",
        "app.tasks.nlp_tasks",
        "app.tasks.contact_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Task routing
    task_routes={
        "app.tasks.scraping_tasks.*": {"queue": "scraping"},
        "app.tasks.nlp_tasks.*": {"queue": "nlp"},
        "app.tasks.contact_tasks.*": {"queue": "contact"},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
    
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Rate limiting
    task_default_rate_limit="10/m",
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-tasks": {
            "task": "app.tasks.maintenance_tasks.cleanup_expired_tasks",
            "schedule": 3600.0,  # Every hour
        },
        "update-job-scores": {
            "task": "app.tasks.nlp_tasks.batch_update_job_scores",
            "schedule": 1800.0,  # Every 30 minutes
        },
    },
)

# Configure logging
celery_app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
celery_app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

if __name__ == "__main__":
    celery_app.start()
