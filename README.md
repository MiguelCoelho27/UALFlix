# UALFlix 🎬

UALFlix é um **mini sistema de streaming de vídeo** desenvolvido no âmbito da unidade curricular de **Arquitetura Avançada de Sistemas (AAS)** da Universidade Autónoma de Lisboa.

Este projeto demonstra, de forma prática, a aplicação de conceitos avançados de **sistemas distribuídos**, **comunicação entre serviços**, **virtualização com Docker**, **replicação e resiliência**, e **preparação para cloud computing**.

---

## ✨ Funcionalidades

- 🎞️ **Catálogo de Vídeos**  
  Permite registar, consultar e persistir vídeos com título, descrição e duração.

- 📤 **Upload de Conteúdo**  
  Simula o envio de vídeos, gerando uma resposta de sucesso. Já suporta persistência dos uploads.

- 📺 **Streaming de Vídeos**  
  Serviço funcional que inicia sessões de streaming com base num `video_id`.

- 📡 **Comunicação RESTful entre microserviços**

- 📦 **Serviços isolados em Docker containers**

- ☁️ **Arquitetura preparada para cloud e escalabilidade**

---

## 🧱 Estrutura de Microserviços

- `catalog-service` – Gestão e persistência dos vídeos.
- `upload-service` – Simulação de upload de vídeos.
- `streaming-service` – Inicia sessões de visualização.
- `nginx` – Reverso para entrada HTTP (porta 80).

---

## 🔧 Tecnologias

- **Python 3.11** com Flask
- **Docker + Docker Compose**
- **Nginx** como gateway reverso
- **Bases de dados simuladas em memória**
- **Requisitos em ficheiros `requirements.txt`**

---

## 🚀 Como Executar

```bash
# Clonar o repositório
git clone https://github.com/MiguelCoelho27/UALFlix.git
cd UALFlix

# Executar com Docker
docker-compose up --build
✅ Estado Atual
✔️ Upload funcional e persistente

✔️ Catálogo funcional e persistente

✔️ Streaming funcional

✔️ Nginx a encaminhar pedidos corretamente

🔄 Pronto para testes de desempenho e replicação

📚 Requisitos Académicos
Este projeto cumpre os requisitos definidos pela docente:

✔️ Sistema distribuído com comunicação entre serviços

✔️ Cluster de serviços (upload, catálogo, streaming)

✔️ Virtualização via Docker

✔️ Preparado para execução na cloud

✔️ Simulação de replicação (em desenvolvimento)

✔️ Avaliação de desempenho a integrar