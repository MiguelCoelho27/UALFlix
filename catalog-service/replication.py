import threading
import time
import json
import logging
from queue import Queue
from typing import Dict, Any, Optional
from pymongo import MongoClient
from bson import ObjectId
import redis
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplicationManager:
    """Synchronous and asynchronous replication manager for video metadata"""
    
    def __init__(self):
        # Database connections
        self.primary_mongo = self._connect_mongo("primary")
        self.replica_mongo = self._connect_mongo("replica")
        self.redis_client = self._connect_redis()
        
        # Queue for asynchronous replication
        self.async_queue = Queue()
        self.async_worker_running = False
        
        # Cache settings
        self.CACHE_TTL = 3600  # 1 hour
        self.POPULAR_VIDEOS_KEY = "popular_videos"
        self.CACHE_PREFIX = "video:"
        
        # Consistency
        self.consistency_checks = []
        
        logger.info("ReplicationManager initialized")
    
    def _connect_mongo(self, instance_type: str) -> MongoClient:
        """Connect to different MongoDB instances"""
        if instance_type == "primary":
            uri = os.environ.get("MONGO_PRIMARY_URI", "mongodb://mongo_primary:27017/ualflix")
        else:
            uri = os.environ.get("MONGO_REPLICA_URI", "mongodb://mongo_replica:27017/ualflix")
        
        client = MongoClient(uri)
        db = client.get_database()
        return db["videos"]
    
    def _connect_redis(self) -> redis.Redis:
        """Connect to Redis for caching"""
        redis_host = os.environ.get("REDIS_HOST", "redis")
        redis_port = int(os.environ.get("REDIS_PORT", "6379"))
        
        return redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    
    def start_async_worker(self):
        """Start worker for asynchronous replication"""
        if not self.async_worker_running:
            self.async_worker_running = True
            worker_thread = threading.Thread(target=self._async_worker, daemon=True)
            worker_thread.start()
            logger.info("Asynchronous replication worker started")
    
    def _async_worker(self):
        """Worker that processes asynchronous replication queue"""
        while self.async_worker_running:
            try:
                if not self.async_queue.empty():
                    operation = self.async_queue.get(timeout=1)
                    self._execute_async_replication(operation)
                    self.async_queue.task_done()
                else:
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error in async worker: {e}")
                time.sleep(1)
    
    def _execute_async_replication(self, operation: Dict[str, Any]):
        """Execute an asynchronous replication operation"""
        try:
            op_type = operation["type"]
            data = operation["data"]
            
            if op_type == "create":
                self.replica_mongo.insert_one(data)
                logger.info(f"Async replication: video {data.get('title')} created in replica")
            
            elif op_type == "update":
                video_id = data["_id"]
                update_data = {k: v for k, v in data.items() if k != "_id"}
                self.replica_mongo.update_one(
                    {"_id": ObjectId(video_id)}, 
                    {"$set": update_data}
                )
                logger.info(f"Async replication: video {video_id} updated in replica")
            
            elif op_type == "delete":
                video_id = data["video_id"]
                self.replica_mongo.delete_one({"_id": ObjectId(video_id)})
                logger.info(f"Async replication: video {video_id} removed from replica")
                
        except Exception as e:
            logger.error(f"Error in async replication: {e}")
    
    def replicate_sync(self, operation: str, data: Dict[str, Any]) -> bool:
        """SYNCHRONOUS replication - executes immediately and waits for confirmation"""
        try:
            if operation == "create":
                # Insert in primary database
                result_primary = self.primary_mongo.insert_one(data.copy())
                data["_id"] = result_primary.inserted_id
                
                # Replicate immediately to secondary database
                data_replica = data.copy()
                data_replica["_id"] = ObjectId(str(result_primary.inserted_id))
                self.replica_mongo.insert_one(data_replica)
                
                # Update popular videos cache
                self._update_popular_cache(str(result_primary.inserted_id), data)
                
                logger.info(f"Sync replication COMPLETE: video {data.get('title')} created")
                return str(result_primary.inserted_id)
            
            elif operation == "update":
                video_id = data["video_id"]
                update_data = data["update_data"]
                
                # Update primary database
                result_primary = self.primary_mongo.update_one(
                    {"_id": ObjectId(video_id)}, 
                    {"$set": update_data}
                )
                
                # Replicate immediately
                self.replica_mongo.update_one(
                    {"_id": ObjectId(video_id)}, 
                    {"$set": update_data}
                )
                
                # Invalidate cache
                self._invalidate_cache(video_id)
                
                logger.info(f"Sync replication COMPLETE: video {video_id} updated")
                return result_primary.modified_count > 0
            
            elif operation == "delete":
                video_id = data["video_id"]
                
                # Remove from primary database
                result_primary = self.primary_mongo.delete_one({"_id": ObjectId(video_id)})
                
                # Replicate removal
                self.replica_mongo.delete_one({"_id": ObjectId(video_id)})
                
                # Remove from cache
                self._invalidate_cache(video_id)
                
                logger.info(f"Sync replication COMPLETE: video {video_id} removed")
                return result_primary.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Error in sync replication: {e}")
            return False
    
    def replicate_async(self, operation: str, data: Dict[str, Any]):
        """ASYNCHRONOUS replication - add to queue for later processing"""
        async_operation = {
            "type": operation,
            "data": data,
            "timestamp": time.time()
        }
        self.async_queue.put(async_operation)
        logger.info(f"Operation {operation} added to async queue")
    
    def get_from_cache(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video from Redis cache"""
        try:
            cache_key = f"{self.CACHE_PREFIX}{video_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache HIT for video {video_id}")
                return json.loads(cached_data)
            
            logger.info(f"Cache MISS for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None
    
    def set_cache(self, video_id: str, video_data: Dict[str, Any]):
        """Store video in Redis cache"""
        try:
            cache_key = f"{self.CACHE_PREFIX}{video_id}"
            video_data_copy = video_data.copy()
            
            # Convert ObjectId to string for JSON serialization
            if "_id" in video_data_copy and isinstance(video_data_copy["_id"], ObjectId):
                video_data_copy["_id"] = str(video_data_copy["_id"])
            
            self.redis_client.setex(
                cache_key, 
                self.CACHE_TTL, 
                json.dumps(video_data_copy)
            )
            logger.info(f"Video {video_id} stored in cache")
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
    
    def _invalidate_cache(self, video_id: str):
        """Invalidate cache for a specific video"""
        try:
            cache_key = f"{self.CACHE_PREFIX}{video_id}"
            self.redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for video {video_id}")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    def _update_popular_cache(self, video_id: str, video_data: Dict[str, Any]):
        """Update popular videos cache"""
        try:
            # Add video to popularity ranking
            self.redis_client.zadd(self.POPULAR_VIDEOS_KEY, {video_id: video_data.get("views", 0)})
            
            # Keep only top 50 popular videos
            self.redis_client.zremrangebyrank(self.POPULAR_VIDEOS_KEY, 0, -51)
            
            logger.info(f"Video {video_id} added to popularity ranking")
        except Exception as e:
            logger.error(f"Error updating popular cache: {e}")
    
    def get_popular_videos(self, limit: int = 10) -> list:
        """Get list of popular videos from cache"""
        try:
            # Get IDs of most popular videos (descending order)
            popular_ids = self.redis_client.zrevrange(self.POPULAR_VIDEOS_KEY, 0, limit-1)
            
            popular_videos = []
            for video_id in popular_ids:
                # Try to get from cache first
                video_data = self.get_from_cache(video_id)
                
                if not video_data:
                    # If not in cache, search in database
                    video_data = self.primary_mongo.find_one({"_id": ObjectId(video_id)})
                    if video_data:
                        video_data["_id"] = str(video_data["_id"])
                        self.set_cache(video_id, video_data)
                
                if video_data:
                    popular_videos.append(video_data)
            
            logger.info(f"Returned {len(popular_videos)} popular videos")
            return popular_videos
        except Exception as e:
            logger.error(f"Error getting popular videos: {e}")
            return []
    
    def increment_views(self, video_id: str) -> bool:
        """Increment views and update popularity cache"""
        try:
            # Update in primary database (synchronous)
            result = self.primary_mongo.update_one(
                {"_id": ObjectId(video_id)},
                {"$inc": {"views": 1}}
            )
            
            if result.modified_count > 0:
                # Get updated view count for async replication
                updated_video = self.primary_mongo.find_one({"_id": ObjectId(video_id)})
                current_views = updated_video.get("views", 1) if updated_video else 1
                
                # Update replica (asynchronous) with absolute value
                self.replicate_async("update", {
                    "_id": video_id,
                    "views": current_views
                })
                
                # Update popularity ranking
                self.redis_client.zincrby(self.POPULAR_VIDEOS_KEY, 1, video_id)
                
                # Invalidate video cache to force refresh
                self._invalidate_cache(video_id)
                
                logger.info(f"Views incremented for video {video_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error incrementing views: {e}")
            return False
    
    def check_consistency(self) -> Dict[str, Any]:
        """Check consistency between primary and replica databases"""
        try:
            primary_count = self.primary_mongo.count_documents({})
            replica_count = self.replica_mongo.count_documents({})
            
            # Compare some random records
            inconsistencies = []
            sample_videos = list(self.primary_mongo.find().limit(10))
            
            for video in sample_videos:
                replica_video = self.replica_mongo.find_one({"_id": video["_id"]})
                
                if not replica_video:
                    inconsistencies.append({
                        "video_id": str(video["_id"]),
                        "issue": "Video exists in primary but not in replica"
                    })
                elif video.get("views", 0) != replica_video.get("views", 0):
                    inconsistencies.append({
                        "video_id": str(video["_id"]),
                        "issue": f"Different views: primary={video.get('views')}, replica={replica_video.get('views')}"
                    })
            
            consistency_report = {
                "primary_count": primary_count,
                "replica_count": replica_count,
                "count_match": primary_count == replica_count,
                "inconsistencies": inconsistencies,
                "consistent": len(inconsistencies) == 0 and primary_count == replica_count,
                "check_timestamp": time.time()
            }
            
            logger.info(f"Consistency check: {consistency_report['consistent']}")
            return consistency_report
            
        except Exception as e:
            logger.error(f"Error in consistency check: {e}")
            return {"error": str(e), "consistent": False}

# Global instance of replication manager
replication_manager = ReplicationManager()