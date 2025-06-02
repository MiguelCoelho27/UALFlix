from pymongo import MongoClient
from bson import ObjectId
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/ualflix")
client = MongoClient(MONGO_URI)
db = client.get_database()
videos_collection = db["videos"]

def create_video(title, description, duration, genre, video_url):
    video_data = {
        "title": title,
        "description": description,
        "duration": duration,
        "genre": genre,
        "video_url": video_url,
        "views": 0
    }
    result = videos_collection.insert_one(video_data)
    return str(result.inserted_id)

def get_video_by_id(video_id):
    try:
        video = videos_collection.find_one({"_id": ObjectId(video_id)})
        if video:
            video["_id"] = str(video["_id"])
        return video
    except Exception:
        return None
    
def get_all_videos():
    videos = []
    for video in videos_collection.find():
        video["_id"] = str(video["id"])
        videos.append(video)
    return videos

def increment_view_count(video_id):
    try:
        result = videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$inc": {"views": 1}}
        )
        return result.modified_count > 0
    except Exception:
        return False
    
# Options para Admins
def update_video(video_id, data_update):
    try:
        update_data = {k: v for k, v in data_update.items() if k != "_id"}
        result = videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception:
        return False

def delete_video(video_id):
    try:
        result = videos_collection.delete_one({"_id": ObjectId(video_id)})
        return result.deleted_count > 0
    except Exception:
        return False