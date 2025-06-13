"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Eye } from "lucide-react";

interface Video {
  _id: string;
  title: string;
  description: string;
  genre?: string;
  duration?: number;
  video_url: string;
  views?: number;
  timestamp?: string;
}

export default function CatalogPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoadingVideos, setIsLoadingVideos] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Tracking videos that have been played but not finished
  const viewedVideos = useRef(new Set());

  const fetchVideos = async () => {
    setIsLoadingVideos(true);
    setFetchError(null);
    try {
      const catalogApiUrl =
        process.env.NEXT_PUBLIC_CATALOG_API_URL ||
        "http://localhost/api/catalog";
      const res = await fetch(`${catalogApiUrl}/videos`);

      if (!res.ok) {
        throw new Error("Failed to parse error response from catalog");
      }
      const responseData = await res.json();
      setVideos(responseData.videos || []);
    } catch (err: any) {
      console.error("Error fetching videos:", err);
      setFetchError(err.message || "An unknown error occurred.");
    } finally {
      setIsLoadingVideos(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handlePlay = async (video: Video) => {
    if (viewedVideos.current.has(video._id)) {
      return;
    }
    try {
      const catalogApiUrl =
        process.env.NEXT_PUBLIC_CATALOG_API_URL ||
        "http://localhost/api/catalog";
      await fetch(`${catalogApiUrl}/videos/${video._id}/view`, {
        method: "POST",
      });
      viewedVideos.current.add(video._id);
      setVideos((currentVideos) =>
        currentVideos.map((v) =>
          v._id === video._id ? { ...v, views: (v.views || 0) + 1 } : v
        )
      );
    } catch (error) {
      console.error("Failed to increment view count:", error);
    }
  };

  // This function is called when a video finishes playing.
  const handleEnded = (videoId: string) => {
    // Remove the video from "viewed" allowing it to be counted again on the next play.
    viewedVideos.current.delete(videoId);
    console.log(`Video ${videoId} finished. Ready to count next view.`);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-12">
        <header className="flex flex-col sm:flex-row justify-between items-center py-6 sm:py-8 border-b border-border">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary via-red-500 to-secondary">
              UALFlix Video Catalog
            </h1>
            <p className="text-md sm:text-lg text-muted-foreground mt-1">
              Browse available videos.
            </p>
          </div>
          <Link href="/upload" passHref>
            <Button variant="outline" className="mt-4 sm:mt-0">
              <ArrowLeft className="mr-2 h-4 w-4" /> Go to Upload Page
            </Button>
          </Link>
        </header>

        <section>
          <div className="flex justify-end items-center mb-6">
            <Button
              variant="outline"
              onClick={fetchVideos}
              disabled={isLoadingVideos}
            >
              {isLoadingVideos ? "Refreshing..." : "Refresh Catalog"}
            </Button>
          </div>

          {isLoadingVideos && (
            <div className="text-center text-muted-foreground py-10">
              <p>Loading videos, please wait...</p>
            </div>
          )}
          {fetchError && (
            <div className="text-center text-destructive bg-destructive/10 p-4 rounded-md">
              <p className="font-semibold">Error Loading Videos</p>
              <p>{fetchError}</p>
            </div>
          )}
          {!isLoadingVideos && !fetchError && videos.length === 0 && (
            <div className="text-center text-muted-foreground py-10 border-2 border-dashed border-border rounded-lg p-8">
              <p className="text-lg">No videos available in the catalog yet.</p>
              <p>Try uploading some videos first!</p>
            </div>
          )}

          {!isLoadingVideos && !fetchError && videos.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((video) => (
                <Card
                  key={video._id}
                  className="overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 flex flex-col bg-card"
                >
                  <div className="aspect-video bg-black flex items-center justify-center relative">
                    <video
                      controls
                      className="w-full h-full object-cover"
                      preload="metadata"
                      onPlay={() => handlePlay(video)}
                      onEnded={() => handleEnded(video._id)} // <-- ADD THIS EVENT HANDLER
                    >
                      <source src={video.video_url} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                  <div className="flex flex-col flex-grow">
                    <CardHeader className="p-4">
                      <CardTitle className="text-lg truncate">
                        {video.title}
                      </CardTitle>
                      <CardDescription className="text-xs text-muted-foreground mt-1">
                        {video.genre}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-4 pt-0 flex-grow">
                      <p className="text-sm text-foreground/80 line-clamp-3">
                        {video.description}
                      </p>
                    </CardContent>
                    <CardFooter className="p-4 pt-0">
                      <div className="flex items-center text-xs text-muted-foreground">
                        <Eye className="mr-1.5 h-4 w-4" />
                        {video.views || 0} views
                      </div>
                    </CardFooter>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </section>
        <footer className="text-center py-8 mt-12 border-t border-border">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} UALFlix Catalog.
          </p>
        </footer>
      </div>
    </div>
  );
}
