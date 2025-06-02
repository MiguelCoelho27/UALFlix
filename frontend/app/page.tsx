"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { VideoUploadForm } from "../components/video-upload-form";

interface Video {
  _id: string;
  title: string;
  description: string;
  genre?: string;
  duration?: number;
  video_access_url: string;
  views?: number;
  timestamp?: string;
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoadingVideos, setIsLoadingVideos] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchVideos = async () => {
    setIsLoadingVideos(true);
    setFetchError(null);
    try {
      const catalogApiUrl =
        process.env.NEXT_PUBLIC_CATALOG_API_URL ||
        "http://localhost:5001/videos";
      const res = await fetch(catalogApiUrl);
      if (!res.ok) {
        const errorData = await res
          .json()
          .catch(() => ({ error: "Failed to parse error response" }));
        throw new Error(
          errorData.error ||
            `Failed to fetch videos: ${res.status} ${res.statusText}`
        );
      }
      const data = await res.json();
      setVideos(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error("Error fetching videos:", err);
      setFetchError(
        err.message || "An unknown error occurred while fetching videos."
      );
      setVideos([]);
    } finally {
      setIsLoadingVideos(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handleUploadSuccess = (uploadData: any) => {
    console.log("Upload successful on frontend, server response:", uploadData);
    setTimeout(() => {
      fetchVideos();
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 space-y-12">
        <header className="text-center py-8">
          <h1 className="text-5xl font-extrabold tracking-tight mb-3 bg-clip-text text-transparent bg-gradient-to-r from-primary via-red-500 to-secondary">
            UALFlix 🎬
          </h1>
          <p className="text-xl text-muted-foreground">
            Your Personal Micro-Streaming Platform
          </p>
        </header>

        <section className="max-w-2xl mx-auto">
          <VideoUploadForm onUploadSuccess={handleUploadSuccess} />
        </section>

        <section>
          <h2 className="text-3xl font-semibold mb-6 pb-2 border-b border-border">
            Video Catalog
          </h2>
          {isLoadingVideos && (
            <p className="text-center text-muted-foreground py-4">
              Loading videos...
            </p>
          )}
          {fetchError && (
            <p className="text-center text-destructive py-4">
              Error: {fetchError}
            </p>
          )}
          {!isLoadingVideos && !fetchError && videos.length === 0 && (
            <p className="text-center text-muted-foreground py-4">
              No videos available yet. Try uploading one!
            </p>
          )}
          {!isLoadingVideos && !fetchError && videos.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((video) => (
                <Card
                  key={video._id}
                  className="overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300"
                >
                  <div className="aspect-video bg-muted flex items-center justify-center">
                    {video.video_access_url ? (
                      <video
                        controls
                        className="w-full h-full object-cover"
                        preload="metadata"
                      >
                        <source src={video.video_access_url} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                    ) : (
                      <div className="p-4 text-sm text-destructive-foreground bg-destructive rounded-t-lg">
                        Video URL not available.
                      </div>
                    )}
                  </div>
                  <CardHeader className="p-4">
                    <CardTitle className="text-lg truncate" title={video.title}>
                      {video.title}
                    </CardTitle>
                    <CardDescription className="text-xs text-muted-foreground">
                      {video.genre && (
                        <span className="mr-2">{video.genre}</span>
                      )}
                      {video.timestamp &&
                        `Uploaded: ${new Date(
                          video.timestamp
                        ).toLocaleDateString()}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <p className="text-sm text-foreground/80 line-clamp-3 leading-relaxed">
                      {video.description}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>
        <footer className="text-center py-8 mt-12 border-t border-border">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} UFlix KekW
          </p>
        </footer>
      </div>
    </div>
  );
}
