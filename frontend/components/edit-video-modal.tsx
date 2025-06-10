"use client";

import { useState, useEffect, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Defines the shape of the video data
interface Video {
  _id: string;
  title: string;
  description: string;
  genre?: string;
  video_url: string;
}

interface EditVideoModalProps {
  video: Video | null;
  onClose: () => void;
  onSave: (updatedVideo: Video) => void; // Function to call after a successful save
}

export function EditVideoModal({
  video,
  onClose,
  onSave,
}: EditVideoModalProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    genre: "",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (video) {
      setFormData({
        title: video.title,
        description: video.description,
        genre: video.genre || "",
      });
    }
  }, [video]);

  if (!video) return null; // Don't render the modal if no video is selected for editing

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(`/api/admin/videos/${video._id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || "Failed to update video.");
      }

      onSave(result.video); // Pass the updated video back to the parent
      onClose(); // closes modal
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-card p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4 text-card-foreground">
          Edit Video Details
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="title"
              className="block text-sm font-medium text-foreground/80"
            >
              Title
            </label>
            <Input
              id="title"
              name="title"
              type="text"
              value={formData.title}
              onChange={handleChange}
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
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows={4}
              className="mt-1 block w-full rounded-md border-input bg-background shadow-sm p-2"
            />
          </div>
          <div>
            <label
              htmlFor="genre"
              className="block text-sm font-medium text-foreground/80"
            >
              Genre
            </label>
            <Input
              id="genre"
              name="genre"
              type="text"
              value={formData.genre}
              onChange={handleChange}
              className="mt-1 bg-background"
            />
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <div className="flex justify-end space-x-3 mt-6">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
