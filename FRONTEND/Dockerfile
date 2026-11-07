# Interface image for the local demo (compose.yaml at the repo root).
# Two stages: Node builds the app, then a small nginx serves the built files.
# The final image holds neither Node nor the sources.

FROM node:24-alpine AS build
WORKDIR /app

# Dependencies first: this layer is rebuilt only when the lock file changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# Written into the built files: the address the browser uses to reach the API.
ARG VITE_API_URL=http://localhost:5000
ARG VITE_CALL_CENTER_PHONE=
ENV VITE_API_URL=$VITE_API_URL \
    VITE_CALL_CENTER_PHONE=$VITE_CALL_CENTER_PHONE
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# 5173, like the dev server: the API's CORS_ORIGINS stays the same.
EXPOSE 5173
