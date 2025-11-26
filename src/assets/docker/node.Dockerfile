# Etapa 1: build
FROM node:25-slim AS build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Etapa 2: servir archivos estáticos con Nginx
FROM nginx:alpine-slim

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
