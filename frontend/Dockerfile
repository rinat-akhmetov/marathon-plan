FROM node:20-alpine AS build
WORKDIR /app
COPY package.json vite.config.js ./
COPY src ./src
COPY public/ ./
RUN npm install
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
