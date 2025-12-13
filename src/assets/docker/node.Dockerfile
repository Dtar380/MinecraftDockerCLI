# ────────────── First stage ──────────────
FROM node:25-slim AS build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# ────────────── First stage ──────────────
FROM nginx:alpine-slim

RUN useradd --create-home appUser
USER appUser

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
