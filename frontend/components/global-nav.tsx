"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, Home, Upload, Film, UserCog } from "lucide-react";
import { Button } from "@/components/ui/button";

export function GlobalNav() {
  const [isOpen, setIsOpen] = useState(false);

  const navLinks = [
    { href: "/", icon: Home, label: "Main Page" },
    { href: "/upload", icon: Upload, label: "Upload Video" },
    { href: "/catalog", icon: Film, label: "View Catalog" },
    { href: "/admin", icon: UserCog, label: "Admin Panel" },
  ];

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {isOpen && (
        <div className="bg-card border rounded-lg shadow-lg p-2 mb-2 space-y-1">
          {navLinks.map((link) => (
            <Link key={link.href} href={link.href} passHref>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => setIsOpen(false)}
              >
                <link.icon className="mr-2 h-4 w-4" />
                {link.label}
              </Button>
            </Link>
          ))}
        </div>
      )}

      <Button
        size="icon"
        className="rounded-full h-14 w-14 shadow-lg"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle Navigation Menu"
      >
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </Button>
    </div>
  );
}
