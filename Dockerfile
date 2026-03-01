# Multi-language launcher image (Node, Python, Go)
FROM node:18-bullseye-slim as base
WORKDIR /app

# Install common runtimes
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-pip golang-go ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

COPY . .
RUN chmod +x launcher.sh

# Build Go if project uses it
RUN if [ -f go.mod ]; then \
      echo "Building Go components..."; \
      if go build -o app-bin ./...; then echo "Go build done"; else echo "Go build skipped or failed"; fi; \
    fi

EXPOSE 8080
CMD ["bash", "./launcher.sh"]
