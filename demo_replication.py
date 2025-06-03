#!/usr/bin/env python3
"""
UALFlix - Data Replication Demonstration
========================================

This script demonstrates the implemented replication features:
1. Synchronous vs Asynchronous Replication
2. Popular videos cache
3. Consistency check between replicas
4. Performance with and without cache

Usage: python demo_replication.py
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
CATALOG_BASE_URL = "http://localhost:5001"
DEMO_VIDEOS = [
    {
        "title": "Advanced Python Tutorial",
        "description": "Learn advanced Python concepts for professional development",
        "duration": 1800,
        "genre": "Educational",
        "video_url": "/videos/python_advanced.mp4"
    },
    {
        "title": "Introduction to Microservices", 
        "description": "How to build modern distributed architectures",
        "duration": 2400,
        "genre": "Technical",
        "video_url": "/videos/microservices_intro.mp4"
    },
    {
        "title": "Docker for Developers",
        "description": "Application containerization and orchestration",
        "duration": 1200,
        "genre": "DevOps", 
        "video_url": "/videos/docker_developers.mp4"
    }
]

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"UALFlix {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print formatted section"""
    print(f"\n[INFO] {title}")
    print("-" * 40)

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            print(f"[ERROR] Error {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Connection error: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid response: {response.text}")
        return {"error": "Invalid JSON response"}

def demo_sync_vs_async_replication():
    """Demonstrate differences between synchronous and asynchronous replication"""
    print_section("Synchronous vs Asynchronous Replication")
    
    # Test synchronous replication
    print("[TEST] Creating video with SYNCHRONOUS REPLICATION...")
    sync_video = DEMO_VIDEOS[0].copy()
    sync_video["sync_replication"] = True
    
    sync_start = time.time()
    sync_response = make_request("POST", f"{CATALOG_BASE_URL}/videos", json=sync_video)
    sync_time = time.time() - sync_start
    
    if "error" not in sync_response:
        print(f"[SUCCESS] Video created with synchronous replication in {sync_time:.3f}s")
        print(f"   ID: {sync_response.get('video', {}).get('_id')}")
        print(f"   Type: {sync_response.get('replication_type')}")
    
    # Test asynchronous replication
    print("\n[TEST] Creating video with ASYNCHRONOUS REPLICATION...")
    async_video = DEMO_VIDEOS[1].copy()
    async_video["sync_replication"] = False
    
    async_start = time.time()
    async_response = make_request("POST", f"{CATALOG_BASE_URL}/videos", json=async_video)
    async_time = time.time() - async_start
    
    if "error" not in async_response:
        print(f"[SUCCESS] Video created with asynchronous replication in {async_time:.3f}s")
        print(f"   ID: {async_response.get('video', {}).get('_id')}")
        print(f"   Type: {async_response.get('replication_type')}")
    
    # Performance comparison
    if sync_time > 0 and async_time > 0:
        improvement = ((sync_time - async_time) / sync_time * 100)
        print(f"\n[RESULTS]")
        print(f"   Synchronous Replication:  {sync_time:.3f}s (waits for replica confirmation)")
        print(f"   Asynchronous Replication: {async_time:.3f}s (processes in background)")
        print(f"   Performance improvement: {improvement:.1f}%")
    
    return sync_response.get('video', {}).get('_id'), async_response.get('video', {}).get('_id')

def demo_cache_system(video_ids: list):
    """Demonstrate cache system and popular videos"""
    print_section("Cache System and Popular Videos")
    
    if not video_ids or not video_ids[0]:
        print("[WARNING] Skipping cache demonstration (no valid videos)")
        return
    
    video_id = video_ids[0]
    
    # Simulate views to create popularity
    print("[TEST] Simulating views to create popular videos...")
    for i in range(5):
        response = make_request("POST", f"{CATALOG_BASE_URL}/videos/{video_id}/view")
        if "error" not in response:
            print(f"   View {i+1}: {response.get('current_views')} views")
        time.sleep(0.1)
    
    # Test performance with and without cache
    print(f"\n[TEST] Testing access performance (video {video_id})...")
    
    # Search without cache
    no_cache_start = time.time()
    no_cache_response = make_request("GET", f"{CATALOG_BASE_URL}/videos/{video_id}?cache=false")
    no_cache_time = time.time() - no_cache_start
    
    # Search with cache
    cache_start = time.time()
    cache_response = make_request("GET", f"{CATALOG_BASE_URL}/videos/{video_id}?cache=true")
    cache_time = time.time() - cache_start
    
    if "error" not in no_cache_response and "error" not in cache_response:
        improvement = ((no_cache_time - cache_time) / no_cache_time * 100) if no_cache_time > 0 else 0
        print(f"   Without cache:  {no_cache_time:.4f}s (direct database search)")
        print(f"   With cache:     {cache_time:.4f}s (Redis search)")
        print(f"   Improvement:    {improvement:.1f}%")
    
    # Get popular videos
    print(f"\n[INFO] Most popular videos (from Redis cache):")
    popular_response = make_request("GET", f"{CATALOG_BASE_URL}/videos/popular?limit=5")
    
    if "error" not in popular_response:
        popular_videos = popular_response.get("popular_videos", [])
        for i, video in enumerate(popular_videos, 1):
            print(f"   {i}. {video.get('title')} ({video.get('views', 0)} views)")

def demo_consistency_check():
    """Demonstrate consistency check between replicas"""
    print_section("Consistency Check Between Replicas")
    
    print("[TEST] Checking consistency between primary and replica databases...")
    consistency_response = make_request("POST", f"{CATALOG_BASE_URL}/admin/replication/consistency-check")
    
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

def demo_replication_status():
    """Show complete replication system status"""
    print_section("Replication System Status")
    
    print("[INFO] Getting detailed status...")
    status_response = make_request("GET", f"{CATALOG_BASE_URL}/admin/replication/status")
    
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
        print(f"   Last check:           {'CONSISTENT' if consistency.get('consistent') else 'INCONSISTENT'}")

def demo_advanced_operations():
    """Demonstrate advanced system operations"""
    print_section("Advanced Operations")
    
    # Create video with automatic demo
    print("[TEST] Running automatic demonstration...")
    demo_response = make_request("POST", f"{CATALOG_BASE_URL}/admin/replication/demo", 
                                json={"demo_type": "sync_vs_async"})
    
    if "error" not in demo_response:
        demo_data = demo_response
        print(f"   Demonstration: {demo_data.get('demo')}")
        
        sync_info = demo_data.get("sync_replication", {})
        async_info = demo_data.get("async_replication", {})
        
        print(f"   Sync:  {sync_info.get('time_taken')} - {sync_info.get('description')}")
        print(f"   Async: {async_info.get('time_taken')} - {async_info.get('description')}")
    
    # Clear cache for testing
    print("\n[TEST] Clearing cache for reset...")
    clear_response = make_request("POST", f"{CATALOG_BASE_URL}/admin/cache/clear")
    
    if "error" not in clear_response:
        cleared_keys = clear_response.get("cleared_keys", 0)
        print(f"   Cache cleared: {cleared_keys} keys removed")

def main():
    """Main function that runs all demonstrations"""
    print_header("Data Replication System Demonstration")
    
    print("This script demonstrates the implemented replication features:")
    print("* Synchronous vs Asynchronous Replication")
    print("* Popular videos cache with Redis")
    print("* Consistency check between replicas")
    print("* Performance metrics")
    
    # Check if service is available
    print(f"\n[INFO] Checking connection to {CATALOG_BASE_URL}...")
    health_response = make_request("GET", f"{CATALOG_BASE_URL}/videos")
    
    if "error" in health_response:
        print("[ERROR] Could not connect to catalog service.")
        print("   Make sure the system is running with: docker-compose up")
        sys.exit(1)
    
    print("[SUCCESS] Connection established!")
    
    try:
        # Run demonstrations
        video_ids = demo_sync_vs_async_replication()
        demo_cache_system(video_ids)
        demo_consistency_check()
        demo_replication_status()
        demo_advanced_operations()
        
        print_header("Demonstration Complete")
        print("[SUCCESS] All replication features have been demonstrated!")
        print("\nFor more details, check:")
        print(f"   * Replication status:        {CATALOG_BASE_URL}/admin/replication/status")
        print(f"   * Popular videos:            {CATALOG_BASE_URL}/videos/popular")
        print(f"   * Redis Commander:           http://localhost:8081")
        print(f"   * Mongo Express (primary):   http://localhost:8082")
        print(f"   * Mongo Express (replica):   http://localhost:8083")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Demonstration interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()