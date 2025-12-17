FROM node:lts-bullseye-slim as builder  

# Install envsubst
RUN apt-get update && apt-get install -y gettext-base

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

RUN npm run build

# Production stage
FROM nginx:latest

# Copy the built assets to the admin subdirectory
COPY --from=builder /app/dist /usr/share/nginx/html/admin

# Copy custom nginx configuration - THIS IS IMPORTANT
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY entrypoint.sh /docker-entrypoint.d/40-config-env.sh
RUN chmod +x /docker-entrypoint.d/40-config-env.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]