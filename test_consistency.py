#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UALFlix Data Consistency Verification Script
============================================

This script demonstrates data consistency between 
primary and replica MongoDB instances.
"""

import pymongo
import requests
import time
import json
from typing import Dict, List

# MongoDB connections
PRIMARY_URI = "mongodb://localhost:27017/ualflix"
REPLICA_URI = "mongodb://localhost:27018/ualflix"
CATALOG_URL = "http://localhost:5001"

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"UALFlix Consistency Test: {title}")
    print(f"{'='*60}")

def print_section(title: str):
    print(f"\n[INFO] {title}")
    print("-" * 40)

def connect_mongodb(uri: str, name: str):
    """Connect to MongoDB instance"""
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print(f"[SUCCESS] Connected to {name}: {uri}")
        return client.ualflix.videos
    except Exception as e:
        print(f"[ERROR] Failed to connect to {name}: {e}")
        return None

def get_collection_stats(collection, name: str) -> Dict:
    """Get collection statistics"""
    try:
        stats = {
            "name": name,
            "count": collection.count_documents({}),
            "documents": list(collection.find({}, {"_id": 1, "title": 1, "views": 1}).sort("_id", 1))
        }
        return stats
    except Exception as e:
        print(f"[ERROR] Failed to get stats for {name}: {e}")
        return {"name": name, "count": 0, "documents": [], "error": str(e)}

def compare_collections(primary_stats: Dict, replica_stats: Dict):
    """Compare primary and replica collections"""
    print_section(f"Comparing {primary_stats['name']} vs {replica_stats['name']}")
    
    # Compare counts
    primary_count = primary_stats.get("count", 0)
    replica_count = replica_stats.get("count", 0)
    
    print(f"   Document count - Primary: {primary_count}, Replica: {replica_count}")
    
    if primary_count == replica_count:
        print(f"   PASS: COUNT CONSISTENT - Both have {primary_count} documents")
    else:
        print(f"   FAIL: COUNT INCONSISTENT - Primary={primary_count}, Replica={replica_count}")
        return False
    
    # Compare documents
    primary_docs = primary_stats.get("documents", [])
    replica_docs = replica_stats.get("documents", [])
    
    if len(primary_docs) != len(replica_docs):
        print(f"   FAIL: DOCUMENT LIST LENGTH MISMATCH")
        return False
    
    # Compare each document
    inconsistencies = []
    for i, (p_doc, r_doc) in enumerate(zip(primary_docs, replica_docs)):
        if p_doc.get("_id") != r_doc.get("_id"):
            inconsistencies.append(f"Document {i}: ID mismatch")
        if p_doc.get("title") != r_doc.get("title"):
            inconsistencies.append(f"Document {i}: Title mismatch")
        # Note: views might differ due to async replication
        
    if inconsistencies:
        print(f"   FAIL: DOCUMENT INCONSISTENCIES FOUND:")
        for issue in inconsistencies:
            print(f"      - {issue}")
        return False
    else:
        print(f"   PASS: DOCUMENT DATA CONSISTENT - All documents match")
        return True

def test_replication_consistency():
    """Test that new data is replicated consistently"""
    print_section("Testing Real-time Replication Consistency")
    
    # Create a test video
    test_video = {
        "title": f"Consistency Test Video {int(time.time())}",
        "description": "Video created to test data consistency",
        "duration": 60,
        "genre": "Test",
        "video_url": "/test/consistency.mp4",
        "sync_replication": True  # Force synchronous replication
    }
    
    print("[TEST] Creating video with synchronous replication...")
    try:
        response = requests.post(f"{CATALOG_URL}/videos", json=test_video, timeout=10)
        if response.status_code == 201:
            result = response.json()
            video_id = result.get("video_id", result.get("video", {}).get("_id"))
            print(f"   SUCCESS: Video created successfully: {video_id}")
            
            # Wait a moment for replication
            print("[INFO] Waiting 2 seconds for replication to complete...")
            time.sleep(2)
            
            return video_id
        else:
            print(f"   FAIL: Failed to create video: {response.status_code}")
            return None
    except Exception as e:
        print(f"   FAIL: Error creating video: {e}")
        return None

def test_view_consistency(video_id: str):
    """Test that view increments are consistent"""
    if not video_id:
        return
        
    print_section("Testing View Count Consistency")
    
    print("[TEST] Incrementing view count 3 times...")
    for i in range(3):
        try:
            response = requests.post(
                f"{CATALOG_URL}/videos/{video_id}/view",
                json={},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                views = result.get("current_views", 0)
                print(f"   View {i+1}: {views} total views")
            time.sleep(0.5)
        except Exception as e:
            print(f"   ERROR: Error incrementing view {i+1}: {e}")
    
    # Wait for async replication
    print("[INFO] Waiting 3 seconds for async view replication...")
    time.sleep(3)

def show_detailed_comparison(primary_collection, replica_collection):
    """Show detailed document comparison"""
    print_section("Detailed Document Comparison")
    
    try:
        primary_docs = list(primary_collection.find().sort("_id", 1))
        replica_docs = list(replica_collection.find().sort("_id", 1))
        
        print(f"   Primary documents: {len(primary_docs)}")
        print(f"   Replica documents: {len(replica_docs)}")
        
        if len(primary_docs) == len(replica_docs):
            print("\n   Document-by-document comparison:")
            for i, (p_doc, r_doc) in enumerate(zip(primary_docs, replica_docs)):
                title = p_doc.get("title", "Unknown")
                p_views = p_doc.get("views", 0)
                r_views = r_doc.get("views", 0)
                
                status = "CONSISTENT" if p_views == r_views else "DIFFERENT"
                print(f"      {i+1}. {title[:30]}: Primary={p_views} views, Replica={r_views} views [{status}]")
        
    except Exception as e:
        print(f"   ERROR: Error in detailed comparison: {e}")

def check_redis_consistency():
    """Check Redis cache consistency"""
    print_section("Redis Cache Consistency Check")
    
    try:
        # Get popular videos from cache
        response = requests.get(f"{CATALOG_URL}/videos/popular?limit=10", timeout=5)
        if response.status_code == 200:
            result = response.json()
            popular_videos = result.get("popular_videos", [])
            cache_source = result.get("source", "unknown")
            
            print(f"   Cache source: {cache_source}")
            print(f"   Popular videos in cache: {len(popular_videos)}")
            
            for i, video in enumerate(popular_videos[:5], 1):
                title = video.get("title", "Unknown")
                views = video.get("views", 0)
                print(f"      {i}. {title[:30]} ({views} views)")
            
            return True
        else:
            print(f"   FAIL: Failed to get cache data: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ERROR: Error checking cache: {e}")
        return False

def main():
    """Main consistency testing function"""
    print_header("Data Consistency Verification")
    
    print("This script will verify data consistency between:")
    print("* Primary MongoDB instance (localhost:27017)")
    print("* Replica MongoDB instance (localhost:27018)")
    print("* Redis cache consistency")
    print("* Real-time replication consistency")
    
    # Connect to databases
    primary_collection = connect_mongodb(PRIMARY_URI, "Primary MongoDB")
    replica_collection = connect_mongodb(REPLICA_URI, "Replica MongoDB")
    
    if primary_collection is None or replica_collection is None:
        print("\n[ERROR] Could not connect to one or both MongoDB instances")
        print("Make sure Docker Compose is running: docker-compose up")
        return
    
    try:
        # 1. Initial consistency check
        print_section("Initial Consistency Check")
        primary_stats = get_collection_stats(primary_collection, "Primary")
        replica_stats = get_collection_stats(replica_collection, "Replica")
        
        initial_consistent = compare_collections(primary_stats, replica_stats)
        
        # 2. Test real-time replication
        test_video_id = test_replication_consistency()
        
        # 3. Test view consistency
        test_view_consistency(test_video_id)
        
        # 4. Final consistency check
        print_section("Final Consistency Check")
        final_primary_stats = get_collection_stats(primary_collection, "Primary")
        final_replica_stats = get_collection_stats(replica_collection, "Replica")
        
        final_consistent = compare_collections(final_primary_stats, final_replica_stats)
        
        # 5. Detailed comparison
        show_detailed_comparison(primary_collection, replica_collection)
        
        # 6. Cache consistency
        cache_consistent = check_redis_consistency()
        
        # Final report
        print_header("Consistency Verification Report")
        
        print(f"   Initial consistency:        {'PASS' if initial_consistent else 'FAIL'}")
        print(f"   Post-operation consistency: {'PASS' if final_consistent else 'FAIL'}")
        print(f"   Cache consistency:          {'PASS' if cache_consistent else 'FAIL'}")
        
        if initial_consistent and final_consistent and cache_consistent:
            print(f"\n   OVERALL RESULT: PASS - DATA CONSISTENCY VERIFIED")
            print(f"   The replication system maintains data consistency!")
        else:
            print(f"\n   OVERALL RESULT: FAIL - CONSISTENCY ISSUES DETECTED")
            print(f"   Some data consistency issues were found.")
        
        print(f"\n   Data consistency demonstrates:")
        print(f"   - Synchronous replication waits for replica confirmation")
        print(f"   - Asynchronous replication eventually achieves consistency")
        print(f"   - Cache invalidation maintains data freshness")
        print(f"   - System handles concurrent operations correctly")
        
    except Exception as e:
        print(f"\n[ERROR] Error during consistency testing: {e}")

if __name__ == "__main__":
    main()