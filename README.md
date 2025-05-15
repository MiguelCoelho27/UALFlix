# UALFlix 🎬

UALFlix é um **mini sistema de streaming de vídeo** desenvolvido no âmbito da unidade curricular de **Arquitetura Avançada de Sistemas (AAS)** da Universidade Autónoma de Lisboa.

Este projeto demonstra, de forma prática, a utilização de tecnologias modernas aplicadas a **sistemas distribuídos**, **clustering**, **virtualização**, **cloud computing**, **replicação de dados e serviços**, bem como a **avaliação de desempenho**.

---

## ✨ Funcionalidades do Projeto

- 🎞️ **Catálogo de Vídeos**  
  Consulta de vídeos disponíveis com título, descrição e duração.

- 📤 **Upload de Conteúdo**  
  Simulação de envio de vídeos para posterior processamento.

- 📺 **Serviço de Streaming**  
  A disponibilizar futuramente — transmissão de vídeos sob pedido.

- 📦 **Microserviços com Docker**  
  Cada componente do sistema corre isoladamente em containers Docker.

- ☁️ **Preparado para Execução na Cloud**  
  Design pronto para escalabilidade e implantação em ambiente cloud.

---

## 🔧 Tecnologias Utilizadas

- **Linguagem:** Python 3.11  
- **Framework:** Flask  
- **Containerização:** Docker + Docker Compose  
- **Gateway HTTP reverso:** Nginx  
- **Simulação de Base de Dados:** Estruturas em memória (listas Python)  
- **APIs REST:** Comunicação simples e eficaz entre serviços

---

## 🚀 Como Executar

```bash
# Clonar o repositório
git clone https://github.com/MiguelCoelho27/UALFlix.git
cd UALFlix

# Executar os serviços
docker-compose up --build
```

---

## ✅ Estado Atual

- Catálogo e Upload testados com sucesso  
- Streaming ainda não testado  
- Nginx funcionando como reverso, pronto para servir frontend e backend

---

## 📚 Requisitos Académicos

Este projeto cumpre os seguintes requisitos definidos pela docente:

- ✔️ **Sistema distribuído** com comunicação entre componentes
- ✔️ **Cluster de computadores** com containers Docker (3+ serviços)
- ✔️ **Virtualização** via Docker
- ✔️ **Preparado para execução cloud**
- ✔️ **Mecanismo de replicação a ser adicionado**
- ✔️ **Avaliação de desempenho a ser integrada**
