"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { AddVideoForm } from "@/components/add-video-form";
import { Toaster } from "@/components/ui/sonner";

export default function AdminPage() {
  const handleSuccess = (data: any) => {
    <Toaster />;
    console.log("Successfully added new video:", data);
    alert("Video added successfully to the catalog!");
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-12">
        <header className="flex flex-col sm:flex-row justify-between items-center py-6 sm:py-8 border-b border-border">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">
              UALFlix Admin Panel
            </h1>
            <p className="text-md sm:text-lg text-muted-foreground mt-1">
              Manage video catalog metadata.
            </p>
          </div>
          <Link href="/catalog" passHref>
            <Button variant="outline" className="mt-4 sm:mt-0">
              <ArrowLeft className="mr-2 h-4 w-4" /> Go to Catalog
            </Button>
          </Link>
        </header>

        <section className="max-w-2xl mx-auto">
          <AddVideoForm onAddSuccess={handleSuccess} />
        </section>

        <footer className="text-center py-8 mt-12 border-t border-border">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} UALFlix Admin.
          </p>
        </footer>
      </div>
    </div>
  );
}
