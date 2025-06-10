"use client";

import { useState, FormEvent, ChangeEvent, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface AddVideoFormProps {
  onAddSuccess?: (data: any) => void;
}

// File Upload Just like in Upload Form
export function AddVideoForm({ onAddSuccess }: AddVideoFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [genre, setGenre] = useState("");
  const [videoFile, setVideoFile] = useState<File | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setVideoFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!videoFile || !title || !description) {
      setMessage({
        type: "error",
        text: "Please fill in title, description, and select a video file.",
      });
      return;
    }

    setIsSubmitting(true);
    setMessage(null);

    const formData = new FormData();
    formData.append("file", videoFile);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("genre", genre);

    const uploadApiUrl = "/api/upload";

    try {
      const response = await fetch(uploadApiUrl, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setMessage({
          type: "success",
          text: result.message || "Video uploaded and added to catalog!",
        });
        // Clear form
        setTitle("");
        setDescription("");
        setGenre("");
        setVideoFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";

        if (onAddSuccess) {
          onAddSuccess(result);
        }
      } else {
        setMessage({
          type: "error",
          text: result.error || "Failed to upload video.",
        });
      }
    } catch (error) {
      console.error("Submit error:", error);
      setMessage({ type: "error", text: "An unexpected error occurred." });
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
        Add New Video by Uploading
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

      <div>
        <label
          htmlFor="videoFile"
          className="block text-sm font-medium text-foreground/80"
        >
          Video File
        </label>
        <Input
          id="videoFile"
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="video/mp4,video/quicktime,video/x-matroska,video/x-msvideo"
          required
          className="mt-1 bg-background"
        />
        {videoFile && (
          <p className="text-xs text-muted-foreground mt-1">
            Selected: {videoFile.name}
          </p>
        )}
      </div>

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Uploading..." : "Upload and Add Video"}
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
