#!/bin/bash

echo "🚀 A iniciar o túnel de acesso para o Prometheus..."
echo "Mantenha este terminal aberto."
echo "O  browser abre com o URL correto."

minikube service prometheus-service -p ualflix-cluster