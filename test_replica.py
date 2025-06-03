#!/usr/bin/env python3
"""
UALFlix Docker Compose Demonstration
====================================

This script demonstrates the custom replication implementation
running on Docker Compose.

Usage: python demo_docker_compose.py
"""

import requests
import time
import json
import sys
from typing import Dict, Any

# Configuration for Docker Compose
CATALOG_SERVICE_URL = "http://localhost:5001"  # Docker Compose port

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"UALFlix Docker Compose Demo: {title}")
    print(f"{'='*70}")

def print_section(title: str):
    """Print formatted section"""
    print(f"\n[INFO] {title}")
    print("-" * 50)

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        
        if response.status_code >= 400:
            print(f"[ERROR] HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Connection error: {e}")
        return {"error": str(e)}

def demo_implementation_detection():
    """Show which implementation is being used"""
    print_section("Implementation Detection")
    
    print("[INFO] Checking which replication implementation is active...")
    impl_response = make_request("GET", f"{CATALOG_SERVICE_URL}/admin/implementation-info")
    
    if "error" not in impl_response:
        implementation = impl_response.get("implementation", "unknown")
        mongo_uri = impl_response.get("mongo_uri", "unknown")
        features = impl_response.get("features", {})
        
        print(f"   Implementation: {implementation}")
        print(f"   MongoDB URI:    {mongo_uri}")
        print(f"   Features:")
        for feature, enabled in features.items():
            status = "ENABLED" if enabled else "DISABLED"
            print(f"      - {feature}: {status}")
    else:
        print("[ERROR] Could not retrieve implementation info")
        return False
    return True

def demo_custom_replication():
    """Demonstrate custom replication strategies"""
    print_section("Custom Replication Strategies Demo")
    
    print("[INFO] Testing custom synchronous vs asynchronous replication...")
    
    # Test synchronous replication
    print(f"\n[TEST] Creating video with SYNCHRONOUS custom replication...")
    sync_video = {
        "title": "Docker Compose Sync Demo",
        "description": "Video created with custom synchronous replication",
        "duration": 180,
        "genre": "Educational",
        "video_url": "/videos/dc_sync.mp4",
        "sync_replication": True
    }
    
    sync_start = time.time()
    sync_response = make_request("POST", f"{CATALOG_SERVICE_URL}/videos", json=sync_video)
    sync_time = time.time() - sync_start
    
    if "error" not in sync_response:
        print(f"[SUCCESS] Video created with custom sync replication in {sync_time:.3f}s")
        print(f"   Strategy: {sync_response.get('replication_type')}")
        print(f"   Video ID: {sync_response.get('video_id', sync_response.get('video', {}).get('_id'))}")
    
    # Test asynchronous replication
    print(f"\n[TEST] Creating video with ASYNCHRONOUS custom replication...")
    async_video = {
        "title": "Docker Compose Async Demo",
        "description": "Video created with custom asynchronous replication",
        "duration": 180,
        "genre": "Educational", 
        "video_url": "/videos/dc_async.mp4",
        "sync_replication": False
    }
    
    async_start = time.time()
    async_response = make_request("POST", f"{CATALOG_SERVICE_URL}/videos", json=async_video)
    async_time = time.time() - async_start
    
    if "error" not in async_response:
        print(f"[SUCCESS] Video created with custom async replication in {async_time:.3f}s")
        print(f"   Strategy: {async_response.get('replication_type')}")
        print(f"   Video ID: {async_response.get('video_id', async_response.get('video', {}).get('_id'))}")
    
    # Performance comparison
    if sync_time > 0 and async_time > 0:
        improvement = ((sync_time - async_time) / sync_time * 100)
        print(f"\n[RESULTS] Custom Replication Performance Comparison:")
        print(f"   Synchronous:  {sync_time:.3f}s - Waits for replica confirmation")
        print(f"   Asynchronous: {async_time:.3f}s - Returns immediately, replicates in background")
        print(f"   Performance:  {improvement:.1f}% faster with async")
    
    sync_id = sync_response.get('video_id', sync_response.get('video', {}).get('_id'))
    async_id = async_response.get('video_id', async_response.get('video', {}).get('_id'))
    return sync_id, async_id

def demo_cache_and_views(video_id: str):
    """Demonstrate cache and popular videos functionality"""
    print_section("Cache and Popular Videos Demo")
    
    if not video_id:
        print("[WARNING] No video ID available for cache demo")
        return
    
    # Simulate some views
    print("[TEST] Simulating video views...")
    for i in range(5):
        view_response = make_request("POST", f"{CATALOG_SERVICE_URL}/videos/{video_id}/view", 
                                   json={}, headers={"Content-Type": "application/json"})
        if "error" not in view_response:
            views = view_response.get("current_views", 0)
            print(f"   View {i+1}: {views} total views")
        time.sleep(0.2)
    
    # Get popular videos
    print(f"\n[TEST] Retrieving popular videos from cache...")
    popular_response = make_request("GET", f"{CATALOG_SERVICE_URL}/videos/popular?limit=5")
    
    if "error" not in popular_response:
        popular_videos = popular_response.get("popular_videos", [])
        cache_source = popular_response.get("source", "unknown")
        
        print(f"[SUCCESS] Retrieved {len(popular_videos)} popular videos")
        print(f"   Source: {cache_source}")
        
        for i, video in enumerate(popular_videos[:3], 1):
            views = video.get("views", 0)
            title = video.get("title", "Unknown")
            print(f"      {i}. {title} ({views} views)")

def demo_replication_status():
    """Show custom replication system status"""
    print_section("Custom Replication System Status")
    
    print("[INFO] Checking custom replication system status...")
    status_response = make_request("GET", f"{CATALOG_SERVICE_URL}/admin/replication/status")
    
    if "error" not in status_response:
        status = status_response.get("replication_status", {})
        
        # Cache status
        cache_info = status.get("cache", {})
        print(f"   Redis connected:      {'YES' if cache_info.get('redis_connected') else 'NO'}")
        print(f"   Videos in cache:      {cache_info.get('popular_videos_count', 0)}")
        
        # Async queue
        queue_size = status.get("async_queue_size", 0)
        print(f"   Async queue:          {queue_size} pending operations")
        
        # Consistency
        consistency = status.get("consistency", {})
        print(f"   Last consistency:     {'OK' if consistency.get('consistent') else 'ISSUES'}")
    else:
        print("[ERROR] Could not retrieve replication status")

def demo_consistency_check():
    """Demonstrate consistency check between primary and replica"""
    print_section("Consistency Check Between Replicas")
    
    print("[TEST] Running consistency check between primary and replica databases...")
    consistency_response = make_request("POST", f"{CATALOG_SERVICE_URL}/admin/replication/consistency-check")
    
    if "error" not in consistency_response:
        consistency = consistency_response.get("consistency_check", {})
        
        print(f"   Primary database: {consistency.get('primary_count')} videos")
        print(f"   Replica database: {consistency.get('replica_count')} videos")
        print(f"   Consistent:       {'YES' if consistency.get('consistent') else 'NO'}")
        
        inconsistencies = consistency.get("inconsistencies", [])
        if inconsistencies:
            print(f"   Inconsistencies found: {len(inconsistencies)}")
            for issue in inconsistencies[:3]:  # Show only first 3
                print(f"      - {issue.get('issue')}")

def main():
    """Main demonstration function"""
    print_header("Custom Replication Implementation")
    
    print("This demonstration shows:")
    print("* Custom synchronous vs asynchronous replication")
    print("* Data consistency between primary and replica databases")
    print("* Redis cache integration for popular videos")
    print("* Performance metrics and monitoring")
    
    # Check service connectivity
    print(f"\n[INFO] Checking connection to catalog service at {CATALOG_SERVICE_URL}...")
    
    if not demo_implementation_detection():
        print(f"[ERROR] Could not connect to catalog service.")
        print("Make sure Docker Compose is running:")
        print("  docker-compose up -d")
        print("  docker-compose ps")
        sys.exit(1)
    
    print("[SUCCESS] Connected to UALFlix Docker Compose cluster!")
    
    try:
        # Run demonstrations
        video_ids = demo_custom_replication()
        demo_cache_and_views(video_ids[0] if video_ids else None)
        demo_consistency_check()
        demo_replication_status()
        
        print_header("Demonstration Complete")
        print("[SUCCESS] All custom replication features demonstrated!")
        
        print("\nFor more details, check:")
        print(f"   * Video catalog:          {CATALOG_SERVICE_URL}/videos")
        print(f"   * Popular videos:         {CATALOG_SERVICE_URL}/videos/popular")
        print(f"   * Replication status:     {CATALOG_SERVICE_URL}/admin/replication/status")
        print(f"   * Redis Commander:        http://localhost:8081")
        print(f"   * Mongo Express (primary): http://localhost:8082")
        print(f"   * Mongo Express (replica): http://localhost:8083")
        
        print("\nThis implementation demonstrates:")
        print("   - Custom synchronous and asynchronous replication")
        print("   - Data consistency between MongoDB instances")
        print("   - Redis cache for performance optimization")
        print("   - Background async queue processing")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Demonstration interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()