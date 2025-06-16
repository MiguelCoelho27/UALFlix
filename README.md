# 🎬 UALFlix – Mini Sistema de Streaming

Pre-Requesites

-- Docker

▶️ Como Executar o Ambiente

Clonar o Repositorio

git clone https://github.com/MiguelCoelho27/UALFlix.git

Ir para a diretoria certa :

    Dentro da main directory, apenas será necessário correr :
        docker-compose up --build -d

Nota: O processo pode demorar vários minutos na primeira vez. E pode ser necessário correr o script mais do que uma vez.

A Aplicação é acessivel pelos:

    http://localhost/ -- Main Page E todas as funcionalides restantes.
    http://localhost:3001 -- Acesso ao grafana // admin / admin
    http://localhost:8081 -- Redis para popularidade  dos videos
    http://localhost:8082 -- Mongo Express Interface -- admin / admin123
    http://localhost:8083 -- Replica Mongo Express -- admin / admin 123
    http://localhost:9090 -- Acesso ao prometheus
