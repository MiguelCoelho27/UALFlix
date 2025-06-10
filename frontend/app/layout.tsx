import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { GlobalNav } from "@/components/global-nav"; // Import the component

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "UALFlix",
  description: "A Mini Streaming System Project",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <GlobalNav /> {/* Add the global navigation here */}
      </body>
    </html>
  );
}
