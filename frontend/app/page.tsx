"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Upload, Film, UserCog } from "lucide-react"; // Some icons for the buttons

export default function MainPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto flex flex-col items-center justify-center px-4 py-8 text-center space-y-12">
        <header className="py-6 sm:py-8">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary via-red-500 to-secondary">
            Welcome to UALFlix 🎬
          </h1>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            Catalogo De Videos
          </p>
        </header>

        <main className="w-full max-w-md space-y-4">
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
        </main>

        <footer className="text-center py-8 mt-12 w-full border-t border-border">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} UALFlix. Projeto de AAS
          </p>
        </footer>
      </div>
    </div>
  );
}
