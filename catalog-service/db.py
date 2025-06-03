from pymongo import MongoClient
from bson import ObjectId
import os
import logging
from replication import replication_manager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Primary database connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo_primary:27017/ualflix")
client = MongoClient(MONGO_URI)
db = client.get_database()
videos_collection = db["videos"]

def create_video(title, description, duration, genre, video_url, use_sync_replication=True):
    """Create video with synchronous or asynchronous replication"""
    video_data = {
        "title": title,
        "description": description,
        "duration": duration,
        "genre": genre,
        "video_url": video_url,
        "views": 0
    }
    
    try:
        if use_sync_replication:
            # SYNCHRONOUS REPLICATION: operation blocks until replica is synchronized
            video_id = replication_manager.replicate_sync("create", video_data)
            logger.info(f"Video created with SYNCHRONOUS replication: {video_id}")
            return video_id
        else:
            # ASYNCHRONOUS REPLICATION: operation returns immediately
            result = videos_collection.insert_one(video_data)
            video_id = str(result.inserted_id)
            
            # Add to asynchronous replication queue
            video_data["_id"] = result.inserted_id
            replication_manager.replicate_async("create", video_data)
            
            logger.info(f"Video created with ASYNCHRONOUS replication: {video_id}")
            return video_id
            
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        return None

def get_video_by_id(video_id, use_cache=True):
    """Get video by ID with cache support"""
    try:
        # Try to get from cache first (if enabled)
        if use_cache:
            cached_video = replication_manager.get_from_cache(video_id)
            if cached_video:
                return cached_video
        
        # If not in cache, search in database
        video = videos_collection.find_one({"_id": ObjectId(video_id)})
        
        if video:
            video["_id"] = str(video["_id"])
            
            # Store in cache for next queries
            if use_cache:
                replication_manager.set_cache(video_id, video)
            
            return video
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting video {video_id}: {e}")
        return None
    
def get_all_videos(use_cache=True):
    """Get all videos with intelligent cache support"""
    try:
        # First, try to get popular videos from cache
        if use_cache:
            popular_videos = replication_manager.get_popular_videos(limit=20)
            
            if popular_videos:
                logger.info(f"Returning {len(popular_videos)} popular videos from cache")
                
                # Complement with recent videos from database
                recent_videos = list(videos_collection.find().sort("_id", -1).limit(10))
                
                # Remove duplicates
                popular_ids = {v["_id"] for v in popular_videos}
                for video in recent_videos:
                    video_id = str(video["_id"])
                    if video_id not in popular_ids:
                        video["_id"] = video_id
                        popular_videos.append(video)
                
                return popular_videos[:30]  # Maximum 30 videos
        
        # Fallback: direct search in database
        videos = []
        for video in videos_collection.find():
            video["_id"] = str(video["_id"])
            videos.append(video)
        
        logger.info(f"Returning {len(videos)} videos from database")
        return videos
        
    except Exception as e:
        logger.error(f"Error getting all videos: {e}")
        return []

def increment_view_count(video_id):
    """Increment view counter with replication and cache"""
    try:
        # Use the replication manager directly for views
        success = replication_manager.increment_views(video_id)
        
        if success:
            logger.info(f"Views incremented successfully for video {video_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error incrementing views for video {video_id}: {e}")
        return False

def update_video(video_id, data_update, use_sync_replication=True):
    """Update video with replication"""
    try:
        if use_sync_replication:
            # SYNCHRONOUS REPLICATION
            success = replication_manager.replicate_sync("update", {
                "video_id": video_id,
                "update_data": data_update
            })
            logger.info(f"Video {video_id} updated with SYNCHRONOUS replication")
            return success
        else:
            # ASYNCHRONOUS REPLICATION
            result = videos_collection.update_one(
                {"_id": ObjectId(video_id)},
                {"$set": data_update}
            )
            
            if result.modified_count > 0:
                # Add to async queue
                replication_manager.replicate_async("update", {
                    "_id": video_id,
                    **data_update
                })
                
                logger.info(f"Video {video_id} updated with ASYNCHRONOUS replication")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"Error updating video {video_id}: {e}")
        return False

def delete_video(video_id, use_sync_replication=True):
    """Delete video with replication"""
    try:
        if use_sync_replication:
            # SYNCHRONOUS REPLICATION
            success = replication_manager.replicate_sync("delete", {
                "video_id": video_id
            })
            logger.info(f"Video {video_id} deleted with SYNCHRONOUS replication")
            return success
        else:
            # ASYNCHRONOUS REPLICATION
            result = videos_collection.delete_one({"_id": ObjectId(video_id)})
            
            if result.deleted_count > 0:
                # Add to async queue
                replication_manager.replicate_async("delete", {
                    "video_id": video_id
                })
                
                logger.info(f"Video {video_id} deleted with ASYNCHRONOUS replication")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {e}")
        return False

def get_popular_videos(limit=10):
    """Get most popular videos from cache"""
    try:
        popular_videos = replication_manager.get_popular_videos(limit)
        logger.info(f"Returning {len(popular_videos)} popular videos")
        return popular_videos
    except Exception as e:
        logger.error(f"Error getting popular videos: {e}")
        return []

def get_replication_status():
    """Get replication and consistency status"""
    try:
        consistency_report = replication_manager.check_consistency()
        
        # Add cache information
        cache_info = {
            "redis_connected": True,
            "popular_videos_count": 0
        }
        
        try:
            cache_info["popular_videos_count"] = replication_manager.redis_client.zcard(
                replication_manager.POPULAR_VIDEOS_KEY
            )
        except:
            cache_info["redis_connected"] = False
        
        return {
            "consistency": consistency_report,
            "cache": cache_info,
            "async_queue_size": replication_manager.async_queue.qsize()
        }
        
    except Exception as e:
        logger.error(f"Error getting replication status: {e}")
        return {"error": str(e)}

# Initialize asynchronous replication worker
def initialize_replication():
    """Initialize replication system"""
    try:
        replication_manager.start_async_worker()
        logger.info("Replication system initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing replication: {e}")

# Auto-initialization
initialize_replication()