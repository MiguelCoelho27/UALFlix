from flask import Flask, request, jsonify
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from pymongo import MongoClient, ReadPreference
from bson import ObjectId
import os
import logging
import time
import json

app = Flask(__name__)
metrics = PrometheusMetrics(app)
CORS(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo_primary:27017/ualflix")
USE_NATIVE_REPLICA_SET = "replicaSet=" in MONGO_URI

# Initialize based on implementation type
if USE_NATIVE_REPLICA_SET:
    logger.info("Using MongoDB Native Replica Set implementation")
    
    # MongoDB Replica Set clients
    client = MongoClient(MONGO_URI, read_preference=ReadPreference.PRIMARY_PREFERRED)
    read_client = MongoClient(MONGO_URI, read_preference=ReadPreference.SECONDARY_PREFERRED)
    
    db = client.get_database()
    read_db = read_client.get_database()
    videos_collection = db["videos"]
    videos_read_collection = read_db["videos"]
    
    # Redis for cache
    try:
        import redis
        REDIS_HOST = os.environ.get("REDIS_HOST", "redis-service")
        redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        REDIS_AVAILABLE = True
        logger.info(f"Redis connected at {REDIS_HOST}")
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        REDIS_AVAILABLE = False
        redis_client = None
    
    CACHE_TTL = 3600
    POPULAR_VIDEOS_KEY = "popular_videos"
    
else:
    logger.info("Using Custom Replication implementation")
    # Import existing implementation
    try:
        import db
        import replication
        CUSTOM_REPLICATION_AVAILABLE = True
    except ImportError as e:
        logger.error(f"Custom replication modules not available: {e}")
        CUSTOM_REPLICATION_AVAILABLE = False

# Helper functions for MongoDB Native Replica Set
def get_from_cache(video_id: str):
    """Get video from Redis cache"""
    if not REDIS_AVAILABLE:
        return None
    try:
        cached_data = redis_client.get(f"video:{video_id}")
        if cached_data:
            logger.info(f"Cache HIT for video {video_id}")
            return json.loads(cached_data)
        logger.info(f"Cache MISS for video {video_id}")
        return None
    except Exception as e:
        logger.error(f"Cache read error: {e}")
        return None

def set_cache(video_id: str, video_data: dict):
    """Store video in Redis cache"""
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.setex(f"video:{video_id}", CACHE_TTL, json.dumps(video_data))
        logger.info(f"Video {video_id} cached")
    except Exception as e:
        logger.error(f"Cache write error: {e}")

def invalidate_cache(video_id: str):
    """Invalidate cache for a specific video"""
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.delete(f"video:{video_id}")
        logger.info(f"Cache invalidated for video {video_id}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")

def update_popularity_cache(video_id: str, views: int = 0):
    """Update popularity ranking in Redis"""
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.zadd(POPULAR_VIDEOS_KEY, {video_id: views})
        # Keep only top 20 popular videos
        redis_client.zremrangebyrank(POPULAR_VIDEOS_KEY, 0, -21)
        logger.info(f"Video {video_id} added to popularity ranking")
    except Exception as e:
        logger.error(f"Popularity cache error: {e}")

# Routes
@app.route('/videos', methods=['POST'])
def create_video_route():
    """Create video - compatible with both implementations"""
    data = request.get_json()
    
    required_fields = ["title", "description", "duration", "genre", "video_url"]
    if not data or not all(k in data for k in required_fields):
        missing = [k for k in required_fields if k not in data]
        return jsonify({"error": f"Missing fields: {', '.join(missing)} are required"}), 400

    if not isinstance(data.get('duration'), (int, float)):
        return jsonify({"error": "Field 'duration' must be a number (e.g., seconds)"}), 400

    # Determine replication strategy
    use_sync = data.get('sync_replication', True)
    
    if USE_NATIVE_REPLICA_SET:
        # Use MongoDB Native Replica Set
        video_data = {
            "title": data['title'],
            "description": data['description'],
            "duration": data['duration'],
            "genre": data['genre'],
            "video_url": data['video_url'],
            "views": 0
        }
        
        write_concern = {"w": "majority", "j": True} if use_sync else {"w": 1}
        
        try:
            start_time = time.time()
            
            collection = db.get_collection("videos", write_concern=write_concern)
            result = collection.insert_one(video_data)
            video_id = str(result.inserted_id)
            
            end_time = time.time()
            
            # Update cache
            update_popularity_cache(video_id, 0)
            
            # Retrieve created video
            created_video = collection.find_one({"_id": result.inserted_id})
            if created_video:
                created_video["_id"] = str(created_video["_id"])
                set_cache(video_id, created_video)
            
            return jsonify({
                "video": created_video,
                "video_id": video_id,
                "replication_type": "native_replica_set",
                "write_concern": "majority" if use_sync else "single_node",
                "time_taken": f"{end_time - start_time:.3f}s",
                "message": f"Video created with MongoDB {'majority' if use_sync else 'single'} write concern"
            }), 201
            
        except Exception as e:
            logger.error(f"Error creating video with native replica set: {e}")
            return jsonify({"error": str(e)}), 500
    
    else:
        # Use custom implementation
        if not CUSTOM_REPLICATION_AVAILABLE:
            return jsonify({"error": "Custom replication not available"}), 500
            
        video_id = db.create_video(
            data['title'], 
            data['description'], 
            data['duration'], 
            data['genre'], 
            data['video_url'],
            use_sync_replication=use_sync
        )
        
        if video_id:
            created_video = db.get_video_by_id(video_id, use_cache=False) 
            return jsonify({
                "video": created_video,
                "video_id": video_id,
                "replication_type": "custom_implementation",
                "strategy": "sync" if use_sync else "async",
                "message": f"Video created with custom {'synchronous' if use_sync else 'asynchronous'} replication"
            }), 201
        else:
            return jsonify({"error": "Failed to create video"}), 500

@app.route('/videos/<video_id>', methods=['GET'])
def get_video_route(video_id):
    """Get video by ID with configurable read preferences"""
    read_source = request.args.get('read_from', 'primary')  # primary, secondary, cache
    use_cache = request.args.get('cache', 'true').lower() == 'true'
    
    if USE_NATIVE_REPLICA_SET:
        try:
            start_time = time.time()
            
            # Try cache first if enabled
            if use_cache:
                cached_video = get_from_cache(video_id)
                if cached_video:
                    end_time = time.time()
                    return jsonify({
                        "video": cached_video,
                        "read_source": "cache",
                        "time_taken": f"{end_time - start_time:.4f}s"
                    })
            
            # Choose collection based on read preference
            if read_source == "secondary":
                collection = videos_read_collection
                logger.info(f"Reading video {video_id} from SECONDARY")
            else:
                collection = videos_collection
                logger.info(f"Reading video {video_id} from PRIMARY")
            
            video = collection.find_one({"_id": ObjectId(video_id)})
            end_time = time.time()
            
            if video:
                video["_id"] = str(video["_id"])
                
                # Store in cache for future requests
                if use_cache:
                    set_cache(video_id, video)
                
                return jsonify({
                    "video": video,
                    "read_source": read_source,
                    "time_taken": f"{end_time - start_time:.4f}s"
                })
            else:
                return jsonify({"error": "Video not found"}), 404
            
        except Exception as e:
            logger.error(f"Error getting video {video_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    else:
        # Use custom implementation
        if not CUSTOM_REPLICATION_AVAILABLE:
            return jsonify({"error": "Custom replication not available"}), 500
            
        video = db.get_video_by_id(video_id, use_cache=use_cache)
        
        if video:
            return jsonify({
                "video": video,
                "read_source": "custom_implementation",
                "from_cache": use_cache,
                "message": "Video retrieved successfully"
            })
        else:
            return jsonify({"error": "Video not found"}), 404

@app.route('/videos/<video_id>', methods=['PUT'])
def update_video_route(video_id):
    """Update the existing video's metadata"""
    data_update = request.get_json()
    if not data_update:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    success = db.update_video(video_id, data_update, use_sync_replication=True)
    
    if success:
        # Return the updated video data
        updated_video = db.get_video_by_id(video_id, use_cache=True)
        return jsonify({"status": "success", "message": "Video updated", "video": updated_video }), 200
    else:
        return jsonify({"error": "Video not found or failed to update"}), 404
    
@app.route('/videos/<video_id>', methods=['DELETE'])
def delete_video_route(video_id):
    """Delete a video from the catalog"""
    success = db.delete_video(video_id, use_sync_replication=True)
    
    if success:
        return jsonify({"status": "success", "message": "Video deleted successfully"}), 200
    else:
        return jsonify({"error": "Video not found or failed to delete"}), 404
    
@app.route('/videos/<video_id>/view', methods=['POST'])
def increment_video_view(video_id):
    """Increment the view count for a specific video."""
    success = db.increment_view_count(video_id)
    if success:
        return jsonify({"status": "success", "message": "View count incremented."}), 200
    else:
        # This could happen if the video_id is not found
        return jsonify({"error": "Failed to increment view count."}), 404

@app.route('/videos', methods=['GET'])
def get_videos_route():
    """Get all videos with configurable read preferences"""
    read_preference = request.args.get('read_from', 'secondary')
    use_cache = request.args.get('cache', 'true').lower() == 'true'
    
    if USE_NATIVE_REPLICA_SET:
        try:
            # Choose collection based on read preference
            collection = videos_read_collection if read_preference == "secondary" else videos_collection
            
            videos = []
            for video in collection.find().limit(50):  # Limit for performance
                video["_id"] = str(video["_id"])
                videos.append(video)
            
            logger.info(f"Retrieved {len(videos)} videos from {read_preference}")
            return jsonify({
                "videos": videos,
                "count": len(videos),
                "read_source": read_preference,
                "cached_optimization": use_cache
            })
            
        except Exception as e:
            logger.error(f"Error getting all videos: {e}")
            return jsonify({"error": str(e)}), 500
    
    else:
        # Use custom implementation
        if not CUSTOM_REPLICATION_AVAILABLE:
            return jsonify({"error": "Custom replication not available"}), 500
            
        videos = db.get_all_videos(use_cache=use_cache)
        
        return jsonify({
            "videos": videos,
            "count": len(videos),
            "cached_optimization": use_cache,
            "message": "Videos retrieved successfully"
        })

@app.route('/videos/<video_id>/view', methods=['POST'])
def increment_view_route(video_id):
    """Increment view counter with configurable write concern"""
    write_concern_param = request.json.get('write_concern', 'majority') if request.json else 'majority'
    
    if USE_NATIVE_REPLICA_SET:
        try:
            # Choose write concern
            if write_concern_param == "majority":
                collection = db.get_collection("videos", write_concern={"w": "majority"})
            else:
                collection = db.get_collection("videos", write_concern={"w": 1})
            
            result = collection.update_one(
                {"_id": ObjectId(video_id)},
                {"$inc": {"views": 1}}
            )
            
            if result.modified_count > 0:
                # Update popularity ranking
                if REDIS_AVAILABLE:
                    redis_client.zincrby(POPULAR_VIDEOS_KEY, 1, video_id)
                
                # Invalidate cache
                invalidate_cache(video_id)
                
                # Get current view count
                updated_video = collection.find_one({"_id": ObjectId(video_id)})
                current_views = updated_video.get("views", 0) if updated_video else 0
                
                logger.info(f"Views incremented for video {video_id} with {write_concern_param} write concern")
                return jsonify({
                    "status": "success",
                    "message": "View count incremented",
                    "current_views": current_views,
                    "write_concern": write_concern_param
                }), 200
            else:
                return jsonify({"error": "Video not found or failed to increment view count"}), 404
                
        except Exception as e:
            logger.error(f"Error incrementing views: {e}")
            return jsonify({"error": str(e)}), 500
    
    else:
        # Use custom implementation
        if not CUSTOM_REPLICATION_AVAILABLE:
            return jsonify({"error": "Custom replication not available"}), 500
            
        success = db.increment_view_count(video_id)
        
        if success:
            updated_video = db.get_video_by_id(video_id, use_cache=False)
            
            return jsonify({
                "status": "success", 
                "message": "View count incremented",
                "current_views": updated_video.get("views", 0) if updated_video else 0,
                "replication": "async_for_performance"
            }), 200
        else:
            return jsonify({"error": "Video not found or failed to increment view count"}), 404


@app.route('/videos/popular', methods=['GET'])
def get_popular_videos_route():
    """Get most popular videos from cache"""
    limit = int(request.args.get('limit', 10))
    
    if USE_NATIVE_REPLICA_SET and REDIS_AVAILABLE:
        try:
            # Get IDs of most popular videos (descending order)
            popular_ids = redis_client.zrevrange(POPULAR_VIDEOS_KEY, 0, limit-1)
            
            popular_videos = []
            for video_id in popular_ids:
                # Try to get from cache first
                video_data = get_from_cache(video_id)
                
                if not video_data:
                    # If not in cache, search in database
                    video_data = videos_collection.find_one({"_id": ObjectId(video_id)})
                    if video_data:
                        video_data["_id"] = str(video_data["_id"])
                        set_cache(video_id, video_data)
                
                if video_data:
                    popular_videos.append(video_data)
            
            logger.info(f"Returned {len(popular_videos)} popular videos")
            return jsonify({
                "popular_videos": popular_videos,
                "count": len(popular_videos),
                "source": "redis_cache",
                "message": f"Top {limit} popular videos from cache"
            })
            
        except Exception as e:
            logger.error(f"Error getting popular videos: {e}")
            return jsonify({"error": str(e)}), 500
    
    else:
        # Use custom implementation or fallback
        if not CUSTOM_REPLICATION_AVAILABLE:
            return jsonify({"popular_videos": [], "count": 0, "source": "not_available"})
            
        popular_videos = db.get_popular_videos(limit)
        return jsonify({
            "popular_videos": popular_videos,
            "count": len(popular_videos),
            "source": "custom_cache",
            "message": f"Top {limit} popular videos from custom cache"
        })

@app.route('/admin/replica-status', methods=['GET'])
def get_replica_status():
    """Get MongoDB replica set status (only for native replica set)"""
    if not USE_NATIVE_REPLICA_SET:
        return jsonify({"error": "Native replica set not in use"}), 400
    
    try:
        # Get replica set status
        status = db.admin.command("replSetGetStatus")
        
        members = []
        for member in status.get("members", []):
            members.append({
                "name": member.get("name"),
                "state": member.get("stateStr"),
                "health": member.get("health"),
                "is_primary": member.get("stateStr") == "PRIMARY"
            })
        
        return jsonify({
            "replica_set_name": status.get("set"),
            "members": members,
            "ok": status.get("ok") == 1
        })
        
    except Exception as e:
        logger.error(f"Error checking replica status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/implementation-info', methods=['GET'])
def get_implementation_info():
    """Show which implementation is being used"""
    return jsonify({
        "implementation": "native_replica_set" if USE_NATIVE_REPLICA_SET else "custom_replication",
        "mongo_uri": MONGO_URI,
        "redis_available": REDIS_AVAILABLE if USE_NATIVE_REPLICA_SET else None,
        "custom_modules_available": CUSTOM_REPLICATION_AVAILABLE if not USE_NATIVE_REPLICA_SET else None,
        "features": {
            "sync_replication": True,
            "async_replication": True,
            "cache": REDIS_AVAILABLE if USE_NATIVE_REPLICA_SET else (CUSTOM_REPLICATION_AVAILABLE),
            "read_preferences": USE_NATIVE_REPLICA_SET,
            "write_concerns": USE_NATIVE_REPLICA_SET
        }
    })

# Legacy endpoints for backward compatibility
@app.route('/admin/replication/status', methods=['GET'])
def get_replication_status_route():
    """Get replication status (backward compatibility)"""
    if USE_NATIVE_REPLICA_SET:
        # Return native replica set info
        try:
            status = db.admin.command("replSetGetStatus")
            cache_info = {
                "redis_connected": REDIS_AVAILABLE,
                "popular_videos_count": 0
            }
            
            if REDIS_AVAILABLE:
                try:
                    cache_info["popular_videos_count"] = redis_client.zcard(POPULAR_VIDEOS_KEY)
                except:
                    pass
            
            return jsonify({
                "replication_status": {
                    "type": "native_replica_set",
                    "replica_set_name": status.get("set"),
                    "members_count": len(status.get("members", [])),
                    "cache": cache_info
                },
                "message": "Native MongoDB replica set status"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Use custom implementation
        if not CUSTOM_REPLICATION_AVAILABLE:
            return jsonify({"error": "Custom replication not available"}), 500
        
        status = db.get_replication_status()
        return jsonify({
            "replication_status": status,
            "message": "Custom replication status retrieved successfully"
        })

if __name__ == '__main__':
    logger.info(f"UALFlix Catalog Service started with {('MongoDB Native Replica Set' if USE_NATIVE_REPLICA_SET else 'Custom Replication')} implementation")
    app.run(host='0.0.0.0', port=5000, debug=True)