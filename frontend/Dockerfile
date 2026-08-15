FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci \
    && npm cache clean --force
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS production
RUN rm /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/40-generate-runtime-env.sh \
    /docker-entrypoint.d/40-generate-runtime-env.sh
RUN chmod +x /docker-entrypoint.d/40-generate-runtime-env.sh
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]