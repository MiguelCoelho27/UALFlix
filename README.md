# UALFlix – Mini Sistema de Streaming

Projeto de Arquitetura Avançada de Sistemas - UAL 2024/2025.

## Serviços

- **catalog-service**: Gestão de vídeos e metadados.
- **streaming-service**: Entrega de vídeos aos utilizadores.
- **upload-service**: Serviço de uploads com fila assíncrona.
- **nginx**: Balanceador de carga.

## Como correr

```bash
docker-compose up --build
```