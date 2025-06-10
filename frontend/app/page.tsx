"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Upload, Film, UserCog } from "lucide-react";

interface Video {
  _id: string;
  title: string;
  video_url: string;
  genre?: string;
}

function FeaturedVideoCard({ video }: { video: Video }) {
  return (
    <div className="bg-card/50 rounded-lg overflow-hidden border border-border/50 hover:border-primary/50 transition-all hover:scale-105">
      <div className="aspect-video bg-black flex items-center justify-center">
        <video
          src={video.video_url}
          className="w-full h-full object-cover"
          preload="metadata"
          muted
          loop
          playsInline
        ></video>
      </div>
      <div className="p-3">
        <h3 className="font-semibold truncate" title={video.title}>
          {video.title}
        </h3>
        {video.genre && (
          <p className="text-xs text-muted-foreground">{video.genre}</p>
        )}
      </div>
    </div>
  );
}

export default function MainPage() {
  const [featuredVideos, setFeaturedVideos] = useState<Video[]>([]);

  useEffect(() => {
    // Vamos buscar alguns videos para encher a pagina
    const fetchFeaturedVideos = async () => {
      try {
        const res = await fetch("/api/catalog/videos");
        if (!res.ok) return;
        const data = await res.json();
        setFeaturedVideos((data.videos || []).slice(0, 3));
      } catch (error) {
        console.error("Could not fetch featured videos:", error);
      }
    };

    fetchFeaturedVideos();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-grow">
        <div className="container mx-auto flex flex-col items-center justify-center px-4 py-8 text-center space-y-12">
          <header className="py-6 sm:py-8">
            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary via-red-500 to-secondary">
              Welcome to UALFlix 🎬
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
              Plataforma de Videos
            </p>
          </header>

          <div className="w-full max-w-md space-y-4">
            <Link href="/upload" passHref className="block">
              <Button size="lg" className="w-full">
                <Upload className="mr-2 h-5 w-5" /> Upload a New Video
              </Button>
            </Link>
            <Link href="/catalog" passHref className="block">
              <Button size="lg" className="w-full">
                <Film className="mr-2 h-5 w-5" /> Video Catalog
              </Button>
            </Link>
            <Link href="/admin" passHref className="block">
              <Button size="lg" variant="outline" className="w-full">
                <UserCog className="mr-2 h-5 w-5" /> Admin Panel
              </Button>
            </Link>
          </div>

          {/* Featured Videos Section --- Importante para encher a pagina, senao ficava demasiado meh*/}
          {featuredVideos.length > 0 && (
            <section className="w-full max-w-5xl pt-12">
              <h2 className="text-2xl font-bold mb-6">Featured Videos</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {featuredVideos.map((video) => (
                  <Link key={video._id} href="/catalog" passHref>
                    <FeaturedVideoCard video={video} />
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      </main>

      <footer className="text-center py-6 w-full border-t border-border/20">
        <p className="text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} UALFlix. Projeto de AAS
        </p>
      </footer>
    </div>
  );
}
