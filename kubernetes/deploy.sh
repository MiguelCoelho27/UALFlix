#!/bin/bash
set -e

# --- Gestão do Cluster ---
CLUSTER_PROFILE="ualflix-cluster"
echo "🔎 A verificar o estado do cluster Minikube (perfil: $CLUSTER_PROFILE)..."
if ! minikube status -p "$CLUSTER_PROFILE" &> /dev/null; then
  echo "🔥 Cluster não encontrado. A criar um novo cluster Minikube com 3 nós..."
  minikube start --nodes 3 -p "$CLUSTER_PROFILE"
else
  echo "👍 Cluster Minikube '$CLUSTER_PROFILE' já está a correr."
fi
echo "🔌 A ativar o addon 'ingress' no Minikube..."
minikube addons enable ingress -p "$CLUSTER_PROFILE"
echo "✅ Addon 'ingress' ativado."

# --- Deployment da Aplicação UALFlix ---
echo "🚀 A iniciar o deployment da aplicação UALFlix no Kubernetes..."

# 1. iniciar Redis e o StatefulSet do MongoDB
echo "📦 A iniciar Redis e o StatefulSet do MongoloideDB..."
kubectl apply -f redis.yaml
kubectl apply -f mongodb-statefulset.yaml

# 2. ESPERAR que o StatefulSet do MongoDB fique completamente up
echo "⏳ A aguardar que os pods do Mongoloide fiquem prontos..."
kubectl rollout status statefulset/mongodb --timeout=5m
echo "✅ Todos os pods do MongoDB estão prontos!"

# 3. Iniciar o Job de inicialização
echo "📦 A iniciar o Job de inicialização do Mongol..."
kubectl apply -f mongodb-init-job.yaml

echo "⏳ A aguardar que o Job de inicialização do Mong seja concluído..."
kubectl wait --for=condition=complete job/ualflix-mongo-init --timeout=3m
echo "✅ Job do MongoDB concluído!"

# 4. iniciar o resto dos microserviços
echo "📦 A iniciar os serviços da aplicação (Catalog, Upload, etc.)..."
kubectl apply -f catalog.yaml
kubectl apply -f upload.yaml
kubectl apply -f streaming.yaml
kubectl apply -f admin.yaml
kubectl apply -f frontend.yaml

# 5. Iniciar o NGINX e ESPERAR que fique pronto
echo "📦 A iniciar o NGINX Load Balancer..."
kubectl apply -f nginx.yaml
echo "⏳ A aguardar que o deployment do NGINX fique pronto..."
kubectl rollout status deployment/nginx-service --timeout=3m
echo "✅ Deployment do NGINX concluído!"

# 6. Iniciar O MONITORING 
echo "📦 A iniciar os serviços de Monitoring (Prometheus & Grafana)..."
kubectl apply -f monitoring.yaml
echo "⏳ A aguardar que os deployments de monitoring fiquem prontos..."
kubectl rollout status deployment/prometheus --timeout=3m
kubectl rollout status deployment/grafana --timeout=3m
echo "✅ Serviços de Monitoring concluídos!"

echo "🎉 Deployment completo! A obter os URLs de acesso..."
echo "---"
echo "URL da Aplicação (NGINX):"
minikube service nginx-service -p "$CLUSTER_PROFILE" --url
echo "---"
echo "✅ Scripts de acesso gerados!"