# Default recipe to show available commands
default:
    @just --list

# Start all services in the background
up:
    @docker compose up -d

# Stop and remove containers, networks, and images
down:
    @docker compose down

# Show logs for a specific service (usage: just logs airflow)
logs service:
    @docker compose logs -f {{service}}

# Restart a specific service (usage: just restart airflow)
restart service:
    @docker compose restart {{service}}

# Rebuild and restart services
rebuild:
    @docker compose up -d --build --remove-orphans

# Open a shell inside a running container (usage: just shell airflow)
shell service:
    @docker compose exec -it {{service}} bash

# Check status of containers
ps:
    @docker compose ps
