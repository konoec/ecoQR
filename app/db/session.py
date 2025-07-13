from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import motor.motor_asyncio
from pymongo import MongoClient
from loguru import logger

from app.core.config import settings


# PostgreSQL setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()


# MongoDB setup
mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
mongodb_database = mongodb_client[settings.MONGODB_DB]

# Synchronous MongoDB client for initialization
sync_mongodb_client = MongoClient(settings.MONGODB_URL)
sync_mongodb_database = sync_mongodb_client[settings.MONGODB_DB]


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        yield session


def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb_database


async def init_db():
    """Initialize databases and create tables"""
    try:
        # Import all models to ensure they are registered with SQLAlchemy
        from app.models import user, branch, purchase, recycling, reward, waste_type
        
        logger.info("Creating PostgreSQL tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL tables created successfully")
        
        # Initialize MongoDB collections and indexes
        logger.info("Initializing MongoDB collections...")
        await init_mongodb_collections()
        logger.info("✅ MongoDB collections initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


async def init_mongodb_collections():
    """Initialize MongoDB collections and indexes"""
    # Collections for logs and analytics
    collections = [
        "recycling_events",
        "ai_validations", 
        "user_activities",
        "environmental_metrics",
        "system_logs"
    ]
    
    for collection_name in collections:
        collection = mongodb_database[collection_name]
        
        # Create indexes based on collection type
        if collection_name == "recycling_events":
            await collection.create_index([("user_id", 1), ("timestamp", -1)])
            await collection.create_index([("purchase_id", 1)])
            await collection.create_index([("branch_id", 1), ("timestamp", -1)])
            
        elif collection_name == "ai_validations":
            await collection.create_index([("validation_id", 1)])
            await collection.create_index([("timestamp", -1)])
            await collection.create_index([("accuracy_score", -1)])
            
        elif collection_name == "user_activities":
            await collection.create_index([("user_id", 1), ("timestamp", -1)])
            await collection.create_index([("activity_type", 1)])
            
        elif collection_name == "environmental_metrics":
            await collection.create_index([("date", -1)])
            await collection.create_index([("branch_id", 1), ("date", -1)])
            
        elif collection_name == "system_logs":
            await collection.create_index([("timestamp", -1)])
            await collection.create_index([("level", 1)])


async def close_db_connections():
    """Close database connections"""
    await async_engine.dispose()
    mongodb_client.close()
    sync_mongodb_client.close()
    logger.info("Database connections closed")
