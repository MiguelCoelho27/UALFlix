"use client";

import { useState, FormEvent, ChangeEvent, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
// import { Textarea } from "@/components/ui/textarea";

interface VideoUploadFormProps {
  onUploadSuccess?: (data: any) => void;
}

export function VideoUploadForm({ onUploadSuccess }: VideoUploadFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [genre, setGenre] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      if (
        ![
          "video/mp4",
          "video/quicktime",
          "video/x-matroska",
          "video/x-msvideo",
        ].includes(selectedFile.type)
      ) {
        setMessage({
          type: "error",
          text: "Invalid file type. Please upload MP4, MOV, MKV or AVI.",
        });
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
      const maxSize = 50 * 1024 * 1024;
      if (selectedFile.size > maxSize) {
        setMessage({
          type: "error",
          text: `File is too large. Maximum size is ${
            maxSize / (1024 * 1024)
          }MB.`,
        });
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        return;
      }
      setFile(selectedFile);
      setMessage(null);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file || !title || !description) {
      setMessage({
        type: "error",
        text: "Please fill in all fields and select a video file.",
      });
      return;
    }

    setIsUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("genre", genre);

    const uploadApiUrl =
      process.env.NEXT_PUBLIC_UPLOAD_API_URL || "http://localhost:5003/upload";

    try {
      const response = await fetch(uploadApiUrl, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setMessage({
          type: "success",
          text: result.message || "Video uploaded successfully!",
        });
        setTitle("");
        setDescription("");
        setGenre("");
        setFile(null);

        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }

        if (onUploadSuccess) {
          onUploadSuccess(result);
        }
      } else {
        setMessage({
          type: "error",
          text: result.error || "Failed to upload video.",
        });
      }
    } catch (error) {
      console.error("Upload error:", error);
      setMessage({
        type: "error",
        text: "An unexpected error occurred. Please try again.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 p-6 border rounded-lg shadow-md bg-card"
    >
      <h2 className="text-xl font-semibold text-card-foreground">
        Upload New Video
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
          className="mt-1 block w-full rounded-md border-input bg-background shadow-sm focus:border-primary focus:ring-ring sm:text-sm p-2"
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
          placeholder="e.g., Educational, Comedy, Action"
          className="mt-1 bg-background"
        />
      </div>
      <div>
        <label
          htmlFor="file"
          className="block text-sm font-medium text-foreground/80"
        >
          Video File (MP4, MOV, MKV, AVI)
        </label>
        <Input
          id="file"
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="video/mp4,video/quicktime,video/x-matroska,video/x-msvideo"
          required
          className="mt-1 bg-background"
        />
        {file && (
          <p className="text-xs text-muted-foreground mt-1">
            Selected: {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
          </p>
        )}
      </div>
      <Button type="submit" disabled={isUploading} className="w-full">
        {isUploading ? "Uploading..." : "Upload Video"}
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
