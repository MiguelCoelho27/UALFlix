#!/bin/bash
set -e

CLUSTER_PROFILE="ualflix-cluster"

echo "🧹 A limpar todos os recursos da aplicação ..."

# O comando delete não falha se os ficheiros não existirem
kubectl delete -f .
kubectl delete -f nginx.yaml --ignore-not-found=true
kubectl delete -f frontend.yaml --ignore-not-found=true
kubectl delete -f admin.yaml --ignore-not-found=true
kubectl delete -f streaming.yaml --ignore-not-found=true
kubectl delete -f upload.yaml --ignore-not-found=true
kubectl delete -f catalog.yaml --ignore-not-found=true
kubectl delete -f mongodb.yaml --ignore-not-found=true
kubectl delete -f redis.yaml --ignore-not-found=true
kubectl delete -f . # Em caso algo tenha falhado todos são executados para apagar

# Apagar os dados persistentes também (cuidado: isto apaga todos os vídeos e dados)
echo "⚠️ A apagar PersistentVolumeClaims (todos os dados serão perdidos)..."
kubectl delete pvc upload-pvc --ignore-not-found=true
kubectl delete pvc redis-pvc --ignore-not-found=true
kubectl delete pvc -l app=mongodb --ignore-not-found=true

echo "✅ Recursos da aplicação removidos."
echo ""
echo "🔥 A parar e a apagar o cluster Minikube '$CLUSTER_PROFILE'..."
minikube delete -p "$CLUSTER_PROFILE"

echo "✅ Limpeza completa."