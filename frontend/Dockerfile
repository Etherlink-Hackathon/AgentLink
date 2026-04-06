# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app

# Copy the entire workspace to mirror the exact structure (frontend, docs, etc.)
# This ensures that relative paths like '../../../docs' in sanity.js resolve correctly.
COPY . .

# Install dependencies (using --legacy-peer-deps for vite-plugin-node-stdlib-browser conflict)
RUN cd frontend && npm install --legacy-peer-deps

# Build arguments for Vite (Must be provided before 'npm run build')
ARG VITE_GRAPHQL_URL
ENV VITE_GRAPHQL_URL=$VITE_GRAPHQL_URL
ARG VITE_NETWORK_TYPE=mainnet
ENV VITE_NETWORK_TYPE=$VITE_NETWORK_TYPE
ARG VITE_NODE_ENV=production
ENV VITE_NODE_ENV=$VITE_NODE_ENV
ARG VITE_STATS=TRUE
ENV VITE_STATS=$VITE_STATS
ARG VITE_AMPLITUDE
ENV VITE_AMPLITUDE=$VITE_AMPLITUDE
ARG VITE_VAULT_ADDRESS
ENV VITE_VAULT_ADDRESS=$VITE_VAULT_ADDRESS

# Build the app inside the frontend folder
RUN cd frontend && npm run build

# Production stage: Serve with Nginx
FROM nginx:stable-alpine as production-stage

# Copy the build output from the correct directory
COPY --from=build-stage /app/frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
