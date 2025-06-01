# 🎬 UALFlix – Mini Sistema de Streaming

Projeto académico desenvolvido para a cadeira de **Arquitetura Avançada de Sistemas** da Universidade Autónoma de Lisboa.

## 📦 Descrição

O UALFlix é um sistema distribuído de streaming baseado numa arquitetura de microserviços. Suporta upload de vídeos, catálogo público, visualização via streaming e uma área de administração para gestão de conteúdos.

## 🧱 Arquitetura

O sistema está dividido nos seguintes microserviços:

- **Admin Service**: Gestão de vídeos (CRUD para administradores)
- **Catalog Service**: Exposição pública dos vídeos disponíveis
- **Upload Service**: Receção e armazenamento de novos vídeos
- **Streaming Service**: Fornecimento de vídeos por stream
- **NGINX (reverse proxy)**: Encaminhamento de pedidos e load balancing

Todos os serviços comunicam entre si via HTTP e são orquestrados com Docker Swarm.

## 🧪 Endpoints Disponíveis

### 🔧 Admin Service (`http://localhost:5004`)
- `GET /admin/videos` – Lista todos os vídeos no sistema
- `POST /admin/videos` – Adiciona um novo vídeo (JSON com `title`, `description`, `url`)
- *Futuro*: edição e remoção de vídeos

### 📚 Catalog Service (`http://localhost:5001`)
- `GET /catalog/videos` – Lista de vídeos públicos disponíveis
- `GET /catalog/videos/<id>` – Detalhes de um vídeo específico

### ⬆️ Upload Service (`http://localhost:5002`)
- `POST /upload` – Upload de vídeo com campos `file`, `title`, `description`
- *Nota:* ficheiros são guardados na pasta `videos/`

### 🎥 Streaming Service (`http://localhost:5003`)
- `GET /stream/<video_id>` – Acede ao vídeo via stream

🐳 Como executar
```bash
# Clonar o repositório
git clone https://github.com/MiguelCoelho27/UALFlix.git
cd UALFlix

# Criar rede overlay (caso não exista)
docker network create --driver overlay ualflix_ualflix_net

# Fazer build das imagens
docker build -t ualflix_catalog ./catalog-service
docker build -t ualflix_upload ./upload-service
docker build -t ualflix_streaming ./streaming-service
docker build -t ualflix_admin ./admin-service
docker build -t ualflix_nginx ./nginx

# Lançar os serviços com Docker Swarm
docker stack deploy -c docker-stack.yml ualflix
```

🧪 Testes e Validação
Testa os serviços com ferramentas como curl, Postman ou diretamente via browser:

```bash
curl http://localhost:5001/catalog/videos
curl -X POST http://localhost:5004/admin/videos -H "Content-Type: application/json" -d '{"title": "Exemplo", "description": "Teste", "url": "http://localhost:5003/stream/abc"}'
```
🗃️ Persistência
A persistência dos vídeos está implementada via ficheiros físicos (upload).

O estado do catálogo e registos de vídeos mantêm-se entre reinícios dos containers, desde que os volumes não sejam removidos.

📁 Estrutura do Projeto

UALFlix/
├── admin-service/
├── catalog-service/
├── upload-service/
├── streaming-service/
├── nginx/
└── docker-stack.yml

Cada pasta contém:
- Dockerfile
- app.py (main)
- requirements.txt

✅ Funcionalidades Implementadas
 Upload de vídeos

 Streaming de vídeos

 Catálogo público

 Registo de vídeos na API de administração

 Reverse proxy com NGINX

 Comunicação entre serviços via HTTP

