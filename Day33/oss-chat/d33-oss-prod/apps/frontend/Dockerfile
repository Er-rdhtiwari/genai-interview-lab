# --- build ---
FROM node:20-slim AS build
WORKDIR /app

COPY package.json /app/package.json
RUN npm install

COPY . /app
RUN npm run build

# --- runtime ---
FROM node:20-slim AS runtime
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# next standalone output
COPY --from=build /app/.next/standalone /app
COPY --from=build /app/.next/static /app/.next/static
# COPY --from=build /app/public /app/public 2>/dev/null || true

EXPOSE 3000
CMD ["node", "server.js"]
