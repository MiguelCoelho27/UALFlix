# 🎬 UALFlix – Mini Sistema de Streaming

Pre-Requesites
-- Docker
-- Minikube
-- Kubernetes

▶️ Como Executar o Ambiente

##Clonar o Repositorio
git clone https://github.com/MiguelCoelho27/UALFlix.git

##Ir para a diretoria certa :
cd UALFlix/kubernetes

##Tornar os Scripts Executáveis ( Só uma vez )
chmod +x deploy.sh cleanup.sh grafana.sh prometheus.sh redis.sh

##Executar o Script de Deploy

./deploy.sh

##Nota: O processo pode demorar vários minutos na primeira vez.

A Aplicação está acessivel pelo URL dado

Para abrir as restantes funções :

## Usar estes ficheiros em terminais diferentes para executar. 

grafana.sh prometheus.sh redis.sh

Abrir Terminais diferentes e executar cada ficheiro para Monitorização.

## grafana.sh prometheus.sh redis.sh

Se estiver laggado é porque o Minikube sucks
