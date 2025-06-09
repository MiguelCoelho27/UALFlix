"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Video } from "lucide-react";

interface Video {
  _id: string;
  title: string;
  description: string;
  video_url: string;
}

export default function AdminPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVideos = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/videos");
      if (!res.ok) {
        throw new Error("Failed to fetch videos from the admin service.");
      }
      const data = await res.json();
      setVideos(data.videos || []);
    } catch (err: any) {
      setError(err.message);
      setVideos([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handleDelete = async (videoId: string) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this video entry? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      const res = await fetch(`/api/admin/videos/${videoId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Failed to delete the video.");
      }

      setVideos((currentVideos) =>
        currentVideos.filter((video) => video._id !== videoId)
      );
      alert("Video deleted successfully!");
    } catch (err: any) {
      console.error("Delete error:", err);
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        <header className="flex flex-col sm:flex-row justify-between items-center py-6 sm:py-8 border-b border-border">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">
              UALFlix Admin Panel
            </h1>
            <p className="text-md sm:text-lg text-muted-foreground mt-1">
              Manage video catalog metadata.
            </p>
          </div>
          <Link href="/catalog" passHref>
            <Button variant="outline" className="mt-4 sm:mt-0">
              <Video className="mr-2 h-4 w-4" /> Go to Catalog
            </Button>
          </Link>
        </header>

        <main>
          {isLoading && (
            <p className="text-center text-muted-foreground">
              Loading videos...
            </p>
          )}
          {error && <p className="text-center text-destructive">{error}</p>}
          {!isLoading && !error && (
            <div className="space-y-4">
              {videos.map((video) => (
                <div
                  key={video._id}
                  className="flex items-center justify-between p-4 border rounded-lg bg-card shadow-sm"
                >
                  <div className="flex-grow overflow-hidden mr-4">
                    <p
                      className="font-semibold text-lg truncate text-card-foreground"
                      title={video.title}
                    >
                      {video.title}
                    </p>
                    <p
                      className="text-sm text-muted-foreground truncate"
                      title={video.description}
                    >
                      {video.description}
                    </p>
                    <p
                      className="text-xs text-muted-foreground/70 truncate"
                      title={video.video_url}
                    >
                      {video.video_url}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-blue-500 hover:text-blue-700 hover:bg-blue-100"
                    ></Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500 hover:text-red-700 hover:bg-red-100"
                      onClick={() => handleDelete(video._id)}
                    >
                      <Trash2 className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
