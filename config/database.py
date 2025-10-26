"""Database connections and configurations."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncGraphDatabase
import redis.asyncio as redis
from config.settings import settings


class DatabaseManager:
    """Manages all database connections."""
    
    def __init__(self):
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.neo4j_driver = None
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect_mongo(self):
        """Connect to MongoDB."""
        try:
            self.mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
            await self.mongo_client.admin.command('ping')
            print("✅ MongoDB connected successfully")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    async def connect_neo4j(self):
        """Connect to Neo4j."""
        try:
            self.neo4j_driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_pass)
            )
            await self.neo4j_driver.verify_connectivity()
            print("✅ Neo4j connected successfully")
            return True
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            return False
    
    async def connect_redis(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            await self.redis_client.ping()
            print("✅ Redis connected successfully")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
    
    async def get_health_status(self):
        """Get health status of all databases."""
        mongo_status = "ok" if self.mongo_client else "down"
        neo4j_status = "ok" if self.neo4j_driver else "down"
        redis_status = "ok" if self.redis_client else "down"
        
        return {
            "mongo": mongo_status,
            "neo4j": neo4j_status,
            "redis": redis_status
        }
    
    async def close_all(self):
        """Close all database connections."""
        if self.mongo_client:
            self.mongo_client.close()
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        if self.redis_client:
            await self.redis_client.close()


# Global database manager
db_manager = DatabaseManager()
