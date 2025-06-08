"use client";

import { useState, FormEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface AddVideoFormProps {
  onAddSuccess?: (data: any) => void;
}

export function AddVideoForm({ onAddSuccess }: AddVideoFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [genre, setGenre] = useState("");
  const [duration, setDuration] = useState(0);
  const [videoUrl, setVideoUrl] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!title || !description || !videoUrl || duration <= 0) {
      setMessage({
        type: "error",
        text: "Please fill in all required fields (Title, Description, Duration > 0, Video URL).",
      });
      return;
    }

    setIsSubmitting(true);
    setMessage(null);

    const videoData = {
      title,
      description,
      genre,
      duration,
      video_url: videoUrl, // Ensure field name matches what catalog-service expects
    };

    // The endpoint proxied by NGINX to your admin-service
    const adminApiUrl = "/api/admin/videos";

    try {
      const response = await fetch(adminApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(videoData),
      });

      const result = await response.json();

      if (response.ok) {
        setMessage({
          type: "success",
          text: result.message || "Video added successfully!",
        });
        // Clear form
        setTitle("");
        setDescription("");
        setGenre("");
        setDuration(0);
        setVideoUrl("");

        if (onAddSuccess) {
          onAddSuccess(result);
        }
      } else {
        setMessage({
          type: "error",
          text: result.error || "Failed to add video.",
        });
      }
    } catch (error) {
      console.error("Submit error:", error);
      setMessage({
        type: "error",
        text: "An unexpected error occurred. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 p-6 border rounded-lg shadow-md bg-card"
    >
      <h2 className="text-xl font-semibold text-card-foreground">
        Add New Video to Catalog
      </h2>

      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-foreground/80"
        >
          Title
        </label>
        <Input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter video title"
          required
          className="mt-1 bg-background"
        />
      </div>

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-foreground/80"
        >
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter video description"
          required
          rows={3}
          className="mt-1 block w-full rounded-md border-input bg-background shadow-sm p-2"
        />
      </div>

      <div>
        <label
          htmlFor="videoUrl"
          className="block text-sm font-medium text-foreground/80"
        >
          Video URL
        </label>
        <Input
          id="videoUrl"
          type="text"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="e.g., /static_videos/example.mp4"
          required
          className="mt-1 bg-background"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="duration"
            className="block text-sm font-medium text-foreground/80"
          >
            Duration (seconds)
          </label>
          <Input
            id="duration"
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            required
            className="mt-1 bg-background"
          />
        </div>
        <div>
          <label
            htmlFor="genre"
            className="block text-sm font-medium text-foreground/80"
          >
            Genre (Optional)
          </label>
          <Input
            id="genre"
            type="text"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="e.g., Action"
            className="mt-1 bg-background"
          />
        </div>
      </div>

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Adding..." : "Add Video"}
      </Button>

      {message && (
        <div
          className={`mt-4 p-3 rounded-md text-sm ${
            message.type === "success"
              ? "bg-green-100 text-green-700 border border-green-200"
              : "bg-red-100 text-red-700 border border-red-200"
          }`}
        >
          {message.text}
        </div>
      )}
    </form>
  );
}
