FROM python:3.13-slim

LABEL org.opencontainers.image.source=https://github.com/oriolrius/hello-world
LABEL org.opencontainers.image.description="Simple hello-world web server"
LABEL org.opencontainers.image.licenses=MIT

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the application
RUN uv pip install --system .

# Expose port
EXPOSE 49000

# Run the server
CMD ["hello-world", "--bind", "0.0.0.0", "--port", "49000"]
