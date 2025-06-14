#!/bin/bash

# --- CONFIGURATION ---
DOCKERHUB_USER="iulian169"
VERSION="v1"

# --- SCRIPT ---
echo "--- Building and pushing images for UALFlix ---"

# 1. Catalog Service
echo "Building catalog-service..."
docker build -t $DOCKERHUB_USER/ualflix-catalog:$VERSION ./catalog-service
echo "Pushing catalog-service..."
docker push $DOCKERHUB_USER/ualflix-catalog:$VERSION

# 2. Upload Service
echo "Building upload-service..."
docker build -t $DOCKERHUB_USER/ualflix-upload:$VERSION ./upload-service
echo "Pushing upload-service..."
docker push $DOCKERHUB_USER/ualflix-upload:$VERSION

# 3. Streaming Service
echo "Building streaming-service..."
docker build -t $DOCKERHUB_USER/ualflix-streaming:$VERSION ./streaming-service
echo "Pushing streaming-service..."
docker push $DOCKERHUB_USER/ualflix-streaming:$VERSION

# 4. Admin Service
echo "Building admin-service..."
docker build -t $DOCKERHUB_USER/ualflix-admin:$VERSION ./admin-service
echo "Pushing admin-service..."
docker push $DOCKERHUB_USER/ualflix-admin:$VERSION

# 5. Frontend Service
echo "Building frontend..."
docker build -t $DOCKERHUB_USER/ualflix-frontend:$VERSION ./frontend
echo "Pushing frontend..."
docker push $DOCKERHUB_USER/ualflix-frontend:$VERSION

# 6. NGINX Service
echo "Building nginx..."
docker build -t $DOCKERHUB_USER/ualflix-nginx:$VERSION ./nginx
echo "Pushing nginx..."
docker push $DOCKERHUB_USER/ualflix-nginx:$VERSION

echo "--- All images have been pushed to Docker Hub ---"