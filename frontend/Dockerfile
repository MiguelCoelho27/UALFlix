# Etapa 1: build com Node.js
FROM node:20-alpine AS builder

# Add these lines to receive the build arguments
ARG NEXT_PUBLIC_CATALOG_API_URL
ARG NEXT_PUBLIC_ADMIN_API_URL
ARG NEXT_PUBLIC_UPLOAD_API_URL

# And set them as environment variables for the build process
ENV NEXT_PUBLIC_CATALOG_API_URL=$NEXT_PUBLIC_CATALOG_API_URL
ENV NEXT_PUBLIC_ADMIN_API_URL=$NEXT_PUBLIC_ADMIN_API_URL
ENV NEXT_PUBLIC_UPLOAD_API_URL=$NEXT_PUBLIC_UPLOAD_API_URL

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
# This build command will now have access to the environment variables
RUN npm run build

# Etapa 2: servir conteúdo estático com NGINX
FROM nginx:alpine

COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]