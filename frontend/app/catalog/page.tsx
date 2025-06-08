"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

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

  const fetchVideos = async () => {
    setIsLoadingVideos(true);
    setFetchError(null);
    try {
      const catalogApiUrl =
        process.env.NEXT_PUBLIC_CATALOG_API_URL ||
        "http://localhost:5001/videos";
      const res = await fetch(catalogApiUrl);

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({
          error: "Failed to parse error response from catalog",
        }));
        throw new Error(
          errorData.error ||
            `Failed to fetch videos: ${res.status} ${res.statusText}`
        );
      }
      const responseData = await res.json();
      if (responseData && Array.isArray(responseData.videos)) {
        setVideos(responseData.videos);
      } else if (Array.isArray(responseData)) {
        setVideos(responseData);
        console.warn(
          "Catalog API returned a direct array, but expected an object with a 'videos' property."
        );
      } else {
        console.warn(
          "Received unexpected data format from catalog API:",
          responseData
        );
        setVideos([]);
        setFetchError(
          "Received unexpected data format. Expected an object with a 'videos' array."
        );
      }
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
                    {" "}
                    {}
                    {video.video_url ? (
                      <video
                        controls
                        className="w-full h-full object-cover"
                        preload="auto"
                      >
                        <source src={video.video_url} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-sm text-white bg-red-700">
                        {" "}
                        Video URL was not provided for this item.
                      </div>
                    )}
                  </div>
                  <CardHeader className="p-4">
                    <CardTitle
                      className="text-lg truncate hover:text-primary transition-colors"
                      title={video.title}
                    >
                      {video.title}
                    </CardTitle>
                    <CardDescription className="text-xs text-muted-foreground mt-1">
                      {video.genre && (
                        <span className="inline-block bg-secondary text-secondary-foreground px-2 py-0.5 rounded-full mr-2">
                          {video.genre}
                        </span>
                      )}
                      {video.timestamp &&
                        `Uploaded: ${new Date(
                          video.timestamp
                        ).toLocaleDateString()}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-4 pt-0 flex-grow">
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
            &copy; {new Date().getFullYear()} UALFlix Catalog.
          </p>
        </footer>
      </div>
    </div>
  );
}
