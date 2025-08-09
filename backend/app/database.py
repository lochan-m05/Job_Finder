from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
from app.models.job import JobModel
from app.models.contact import ContactModel
from app.models.user import UserModel
from app.models.scraping_task import ScrapingTaskModel

load_dotenv()

# Database client
client = None
database = None

async def init_database():
    """Initialize database connection and models"""
    global client, database
    
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "job_discovery")
    
    # Create Motor client
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    # Initialize Beanie with document models
    await init_beanie(
        database=database,
        document_models=[
            JobModel,
            ContactModel,
            UserModel,
            ScrapingTaskModel
        ]
    )
    
    print(f"Connected to MongoDB: {database_name}")

async def close_database():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return database
