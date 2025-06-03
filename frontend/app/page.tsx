"use client";

import { useState } from "react"; // No longer need useEffect or fetchVideos here
import Link from "next/link"; // For navigation
import { Button } from "@/components/ui/button";
import { VideoUploadForm } from "../components/video-upload-form"; // Ensure this path is correct
import { Video } from "lucide-react"; // Icon for catalog button

// Video interface might not be needed on this page if not displaying catalog here
// interface Video { ... }

export default function UploadPage() {
  // State for videos, isLoadingVideos, fetchError is removed as catalog is on a separate page.

  const [lastUploadStatus, setLastUploadStatus] = useState<{
    message: string;
    data: any;
  } | null>(null);

  const handleUploadSuccess = (uploadData: any) => {
    console.log("Upload successful on frontend, server response:", uploadData);
    setLastUploadStatus({
      message: "Video uploaded! You can now view it in the catalog.",
      data: uploadData,
    });
    // No need to fetchVideos here, as that's on the catalog page.
    // User will navigate to see the updated catalog.
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-12">
        <header className="text-center py-6 sm:py-8">
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-2 sm:mb-3 bg-clip-text text-transparent bg-gradient-to-r from-primary via-red-500 to-secondary">
            UALFlix 🎬
          </h1>
          <p className="text-lg sm:text-xl text-muted-foreground">
            Upload Your Videos
          </p>
        </header>

        <section className="max-w-2xl mx-auto bg-card shadow-xl rounded-lg p-6">
          <VideoUploadForm onUploadSuccess={handleUploadSuccess} />
          {lastUploadStatus && (
            <div className="mt-6 p-4 bg-green-100 text-green-700 border border-green-200 rounded-md">
              <p className="font-semibold">Upload Complete!</p>
              <p>{lastUploadStatus.message}</p>
              <Link href="/catalog" passHref className="mt-2 inline-block">
                <Button
                  variant="link"
                  className="text-green-700 hover:text-green-800"
                >
                  Go to Catalog
                </Button>
              </Link>
            </div>
          )}
        </section>

        <div className="text-center mt-8">
          <Link href="/catalog" passHref>
            <Button size="lg">
              <Video className="mr-2 h-5 w-5" /> View Video Catalog
            </Button>
          </Link>
        </div>

        <footer className="text-center py-8 mt-12 border-t border-border">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} UALFlix. Project for Advanced
            Systems Architecture.
          </p>
        </footer>
      </div>
    </div>
  );
}
