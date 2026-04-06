# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app

# Install dependencies separately to leverage Docker layer caching
COPY package*.json ./
# Using --legacy-peer-deps to handle vite-plugin-node-stdlib-browser conflict
RUN npm install --legacy-peer-deps

# Copy source and build
COPY . .

# Build-time argument for GraphQL URL
# This will be injected into the static files during 'vite build'
ARG VITE_GRAPHQL_URL
ENV VITE_GRAPHQL_URL=$VITE_GRAPHQL_URL

# Network type (mainnet/testnet)
ARG VITE_NETWORK_TYPE=mainnet
ENV VITE_NETWORK_TYPE=$VITE_NETWORK_TYPE

RUN npm run build

# Production stage: Serve with Nginx
FROM nginx:stable-alpine as production-stage

# Copy the build output to Nginx's default public directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Custom nginx config to handle SPA routing if needed
# (Optional: If you have complex routing, you might need a custom nginx.conf)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
