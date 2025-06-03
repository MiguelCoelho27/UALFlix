from flask import Flask, request, jsonify
from flask_cors import CORS
import db 
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) 

@app.route('/videos', methods=['POST'])
def create_video_route():
    """Create video with synchronous or asynchronous replication option"""
    data = request.get_json()
    
    required_fields = ["title", "description", "duration", "genre", "video_url"]
    if not data or not all(k in data for k in required_fields):
        missing = [k for k in required_fields if k not in data]
        return jsonify({"error": f"Missing fields: {', '.join(missing)} are required"}), 400

    if not isinstance(data.get('duration'), (int, float)):
        return jsonify({"error": "Field 'duration' must be a number (e.g., seconds)"}), 400

    # Determine replication type (default: synchronous)
    use_sync = data.get('sync_replication', True)
    
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
        if created_video:
            return jsonify({
                "video": created_video,
                "replication_type": "sync" if use_sync else "async",
                "message": f"Video created with {'synchronous' if use_sync else 'asynchronous'} replication"
            }), 201
        else:
            return jsonify({"error": "Video created but could not be retrieved"}), 500
    else:
        return jsonify({"error": "Failed to create video in database"}), 500

@app.route('/videos/<video_id>', methods=['GET'])
def get_video_route(video_id):
    """Get video by ID (with automatic cache)"""
    # Parameter to control cache
    use_cache = request.args.get('cache', 'true').lower() == 'true'
    
    video = db.get_video_by_id(video_id, use_cache=use_cache)
    
    if video:
        return jsonify({
            "video": video,
            "from_cache": use_cache,
            "message": "Video retrieved successfully"
        })
    else:
        return jsonify({"error": "Video not found"}), 404

@app.route('/videos', methods=['GET'])
def get_videos_route():
    """Get all videos (intelligent with cache)"""
    use_cache = request.args.get('cache', 'true').lower() == 'true'
    
    videos = db.get_all_videos(use_cache=use_cache)
    
    return jsonify({
        "videos": videos,
        "count": len(videos),
        "cached_optimization": use_cache,
        "message": "Videos retrieved successfully"
    })

@app.route('/videos/<video_id>', methods=['PUT'])
def update_video_route(video_id):
    """Update video with replication"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data for update"}), 400
    
    # Extract replication configuration
    use_sync = data.pop('sync_replication', True)
    
    success = db.update_video(video_id, data, use_sync_replication=use_sync)
    
    if success:
        updated_video = db.get_video_by_id(video_id, use_cache=False)
        if updated_video:
            return jsonify({
                "status": "success", 
                "video": updated_video,
                "replication_type": "sync" if use_sync else "async"
            }), 200
        else:
            return jsonify({"error": "Video updated but could not be retrieved"}), 404
    else:
        existing_video = db.get_video_by_id(video_id, use_cache=False)
        if not existing_video:
            return jsonify({"error": "Video not found, cannot update"}), 404
        return jsonify({"error": "Update operation did not modify the video"}), 400

@app.route('/videos/<video_id>', methods=['DELETE'])
def delete_video_route(video_id):
    """Delete video with replication"""
    # Replication configuration
    use_sync = request.args.get('sync', 'true').lower() == 'true'
    
    success = db.delete_video(video_id, use_sync_replication=use_sync)
    
    if success:
        return jsonify({
            "status": "success", 
            "message": "Video deleted",
            "replication_type": "sync" if use_sync else "async"
        }), 200
    else:
        return jsonify({"error": "Video not found or delete failed"}), 404

@app.route('/videos/<video_id>/view', methods=['POST'])
def increment_view_route(video_id):
    """Increment views (with replication and intelligent cache)"""
    success = db.increment_view_count(video_id)
    
    if success:
        # Get updated video from cache/DB
        updated_video = db.get_video_by_id(video_id, use_cache=False)
        
        return jsonify({
            "status": "success", 
            "message": "View count incremented",
            "current_views": updated_video.get("views", 0) if updated_video else 0,
            "replication": "async_for_performance"
        }), 200
    else:
        return jsonify({"error": "Video not found or failed to increment view count"}), 404

# NEW ENDPOINTS TO DEMONSTRATE REPLICATION

@app.route('/videos/popular', methods=['GET'])
def get_popular_videos_route():
    """Get most popular videos (from Redis cache)"""
    limit = int(request.args.get('limit', 10))
    
    popular_videos = db.get_popular_videos(limit)
    
    return jsonify({
        "popular_videos": popular_videos,
        "count": len(popular_videos),
        "source": "redis_cache",
        "message": f"Top {limit} popular videos from cache"
    })

@app.route('/admin/replication/status', methods=['GET'])
def get_replication_status_route():
    """Get detailed replication and consistency status"""
    status = db.get_replication_status()
    
    return jsonify({
        "replication_status": status,
        "timestamp": status.get("consistency", {}).get("check_timestamp"),
        "message": "Replication status retrieved successfully"
    })

@app.route('/admin/replication/consistency-check', methods=['POST'])
def force_consistency_check_route():
    """Force consistency check between replicas"""
    try:
        from replication import replication_manager
        consistency_report = replication_manager.check_consistency()
        
        return jsonify({
            "consistency_check": consistency_report,
            "forced": True,
            "message": "Consistency check completed"
        })
    except Exception as e:
        logger.error(f"Error in forced consistency check: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/cache/clear', methods=['POST'])
def clear_cache_route():
    """Clear Redis cache (for testing)"""
    try:
        from replication import replication_manager
        
        # Clear individual video cache
        cache_keys = replication_manager.redis_client.keys(f"{replication_manager.CACHE_PREFIX}*")
        if cache_keys:
            replication_manager.redis_client.delete(*cache_keys)
        
        # Clear popularity ranking
        replication_manager.redis_client.delete(replication_manager.POPULAR_VIDEOS_KEY)
        
        return jsonify({
            "status": "success",
            "cleared_keys": len(cache_keys),
            "message": "Cache cleared successfully"
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/replication/demo', methods=['POST'])
def replication_demo_route():
    """Endpoint for demonstrating different replication strategies"""
    demo_type = request.json.get('demo_type', 'sync_vs_async')
    
    try:
        if demo_type == 'sync_vs_async':
            # Demonstration: create video with synchronous replication
            import time
            
            sync_start = time.time()
            sync_video_id = db.create_video(
                "Demo Sync Video", 
                "Video created with synchronous replication", 
                120, 
                "Demo", 
                "/demo/sync.mp4",
                use_sync_replication=True
            )
            sync_time = time.time() - sync_start
            
            # Create video with asynchronous replication
            async_start = time.time()
            async_video_id = db.create_video(
                "Demo Async Video", 
                "Video created with asynchronous replication", 
                120, 
                "Demo", 
                "/demo/async.mp4",
                use_sync_replication=False
            )
            async_time = time.time() - async_start
            
            return jsonify({
                "demo": "sync_vs_async_replication",
                "sync_replication": {
                    "video_id": sync_video_id,
                    "time_taken": f"{sync_time:.3f}s",
                    "description": "Waits for replica confirmation before returning"
                },
                "async_replication": {
                    "video_id": async_video_id,
                    "time_taken": f"{async_time:.3f}s",
                    "description": "Returns immediately, replicates in background"
                },
                "message": "Synchronous vs asynchronous replication demonstration"
            })
        
        elif demo_type == 'cache_performance':
            # Demonstration: performance with and without cache
            video_id = request.json.get('video_id')
            if not video_id:
                return jsonify({"error": "video_id required for cache demo"}), 400
            
            # Search without cache
            no_cache_start = time.time()
            video_no_cache = db.get_video_by_id(video_id, use_cache=False)
            no_cache_time = time.time() - no_cache_start
            
            # Search with cache
            cache_start = time.time()
            video_with_cache = db.get_video_by_id(video_id, use_cache=True)
            cache_time = time.time() - cache_start
            
            return jsonify({
                "demo": "cache_performance",
                "without_cache": {
                    "time_taken": f"{no_cache_time:.4f}s",
                    "source": "database"
                },
                "with_cache": {
                    "time_taken": f"{cache_time:.4f}s",
                    "source": "redis_cache"
                },
                "performance_improvement": f"{((no_cache_time - cache_time) / no_cache_time * 100):.1f}%",
                "message": "Cache performance demonstration"
            })
        
        else:
            return jsonify({"error": "Unknown demo_type. Use 'sync_vs_async' or 'cache_performance'"}), 400
            
    except Exception as e:
        logger.error(f"Error in demonstration: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("UALFlix Catalog Service started with replication system")
    app.run(host='0.0.0.0', port=5000, debug=True)