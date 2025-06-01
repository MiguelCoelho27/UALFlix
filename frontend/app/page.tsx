'use client';
import { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

type Video = {
  title: string;
  url: string;
};

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/catalog/videos")
      .then((res) => res.json())
      .then((data) => setVideos(data))
      .catch((err) => console.error("Erro ao buscar vídeos:", err));
  }, []);

  const handleSubmit = async () => {
    const res = await fetch("http://localhost:5004/admin/videos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, url }),
    });
    if (res.ok) {
      setVideos([...videos, { title, url }]);
      setTitle("");
      setUrl("");
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">UALFlix 🎬</h1>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Adicionar novo vídeo</h2>
        <div className="flex gap-2">
          <Input
            placeholder="Título"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Input
            placeholder="URL do vídeo"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Button onClick={handleSubmit}>Adicionar</Button>
        </div>
      </div>

      <h2 className="text-xl font-semibold mb-4">Catálogo de Vídeos</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {videos.map((video, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <h3 className="font-bold text-lg">{video.title}</h3>
              <video controls className="w-full mt-2">
                <source src={video.url} type="video/mp4" />
                O seu browser não suporta vídeos incorporados.
              </video>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
