# Admin Service - UALFlix 🎬

Este microserviço atua como gateway para o catálogo de vídeos.

## 📌 Função
Faz um proxy entre pedidos para `/admin/videos` e o microserviço `catalog-service`.

## 🚀 Como correr

### Em Docker
```bash
docker build -t admin-service .
docker run --rm -it -p 5004:5004 admin-service