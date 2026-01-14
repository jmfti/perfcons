.PHONY: help build up down restart logs test clean ngrok-url logs-ngrok

# Default target
help:
	@echo "Available commands:"
	@echo "  make build      - Build the Docker images"
	@echo "  make up         - Start the services"
	@echo "  make down       - Stop the services"
	@echo "  make restart    - Restart the services"
	@echo "  make logs       - Show logs from all services"
	@echo "  make logs-api   - Show logs from API service"
	@echo "  make logs-db    - Show logs from database service"
	@echo "  make logs-ngrok - Show logs from ngrok service"
	@echo "  make ngrok-url  - Get the ngrok public URL"
	@echo "  make test       - Run integration tests"
	@echo "  make clean      - Stop services and remove volumes"

# Build Docker images
build:
	docker compose build

# Start services
up:
	docker compose up -d
	@echo "Services started. API available at http://localhost:8000"
	@echo "Swagger docs available at http://localhost:8000/docs"

# Stop services
down:
	docker compose down

# Restart services
restart: down up

# Show logs
logs:
	docker compose logs -f

# Show API logs
logs-api:
	docker compose logs -f api

# Show DB logs
logs-db:
	docker compose logs -f db

# Show ngrok logs
logs-ngrok:
	docker compose logs -f ngrok

# Get ngrok public URL
ngrok-url:
	@echo "Fetching ngrok public URL..."
	@curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
		grep -q '"public_url"' && \
		curl -s http://localhost:4040/api/tunnels | \
		grep -o '"public_url":"https://[^"]*' | \
		head -1 | \
		cut -d'"' -f4 || \
		echo "ngrok tunnel not ready yet. Make sure you have set NGROK_AUTHTOKEN in your .env file and restarted the services."

# Run integration tests
test:
	@echo "Running integration tests..."
	python -m unittest discover -s tests -p "test_*.py" -v

# Clean up everything including volumes
clean:
	docker compose down -v
	@echo "Services stopped and volumes removed"
