#!/bin/bash

echo "🚀 A iniciar o túnel de acesso para o Grafana..."
echo "Mantenha este terminal aberto."
echo "O browser abre com o URL correto. (Login: admin/admin)"

minikube service grafana-service -p ualflix-cluster