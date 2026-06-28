# Multi-stage build for a lean production image.
#
# IMPORTANT: NEXT_PUBLIC_API_URL is inlined into the client JS bundle at
# BUILD time by Next.js (this is how all NEXT_PUBLIC_* vars work — they
# are not read at container start). It must be passed as a build arg, not
# just a runtime environment variable. docker-compose.yml passes it via
# `build.args`.

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-slim AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
