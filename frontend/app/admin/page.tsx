"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Pencil, PlusCircle, Video } from "lucide-react";
import { EditVideoModal } from "@/components/edit-video-modal";
import { AddVideoForm } from "@/components/add-video-form";

interface Video {
  _id: string;
  title: string;
  description: string;
  genre?: string;
  video_url: string;
}

export default function AdminPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for modals
  const [videoToEdit, setVideoToEdit] = useState<Video | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const fetchVideos = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/videos");
      if (!res.ok) throw new Error("Failed to fetch videos.");
      const data = await res.json();
      setVideos(data.videos || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handleDelete = async (videoId: string) => {
    if (!window.confirm("Are you sure you want to delete this video?")) return;
    try {
      const res = await fetch(`/api/admin/videos/${videoId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete video.");
      setVideos((current) => current.filter((video) => video._id !== videoId));
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleSaveEdit = (updatedVideo: Video) => {
    setVideos((current) =>
      current.map((v) => (v._id === updatedVideo._id ? updatedVideo : v))
    );
  };

  const handleAddSuccess = () => {
    setIsAddModalOpen(false);
    fetchVideos();
  };

  return (
    <>
      {videoToEdit && (
        <EditVideoModal
          video={videoToEdit}
          onClose={() => setVideoToEdit(null)}
          onSave={handleSaveEdit}
        />
      )}
      {isAddModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-card p-1 rounded-lg shadow-xl w-full max-w-2xl relative">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsAddModalOpen(false)}
              className="absolute top-2 right-2 h-8 w-8"
            >
              &times;
            </Button>
            <AddVideoForm onAddSuccess={handleAddSuccess} />
          </div>
        </div>
      )}

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
            <div className="flex items-center space-x-2 mt-4 sm:mt-0">
              <Button onClick={() => setIsAddModalOpen(true)}>
                <PlusCircle className="mr-2 h-4 w-4" /> Add New Video
              </Button>
              <Link href="/catalog" passHref>
                <Button variant="outline">
                  <Video className="mr-2 h-4 w-4" /> View Catalog
                </Button>
              </Link>
            </div>
          </header>

          <main>
            {/* Edit Button added guys*/}
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
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setVideoToEdit(video)}
                        className="text-blue-500 hover:text-blue-700 hover:bg-blue-100"
                      >
                        <Pencil className="h-5 w-5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(video._id)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-100"
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
    </>
  );
}
