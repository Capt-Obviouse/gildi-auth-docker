# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker-based deployment of [Alliance Auth](https://allianceauth.org/), an authentication and management system for EVE Online corporations and alliances. The deployment uses a custom Docker image that extends the official Alliance Auth image with additional community plugins.

## Common Commands

### Starting/Stopping Services

```bash
# Start all containers
docker compose up -d

# Start single service
docker compose up -d <service_name>

# Stop all containers
docker compose down
```

### Upgrading Alliance Auth

1. Update the `AA_DOCKER_TAG` version in `.env`
2. Run:
```bash
docker compose pull
docker compose up -d --build
docker compose exec aa_gunicorn bash
allianceauth update myauth
auth migrate
auth collectstatic
```

### Django Management Commands

Use the `aa_cli` container for management commands (the gunicorn container's entrypoint interferes with direct command execution):

```bash
docker compose run --rm aa_cli <command>

# Examples
docker compose run --rm aa_cli migrate
docker compose run --rm aa_cli collectstatic --noinput
docker compose run --rm aa_cli shell_plus
```

### Initial Setup

```bash
# Generate .env file with secure passwords
./scripts/prepare-env.sh
```

## Architecture

### Docker Services

- **aa_gunicorn**: Main web application (Gunicorn WSGI server on port 8000)
- **aa_worker**: Celery workers (2 replicas) for background tasks
- **aa_beat**: Celery beat scheduler for periodic tasks
- **aa_discordbot**: Discord bot integration
- **aa_cli**: CLI container for running manage.py commands
- **auth_mysql**: MariaDB 11.8 database
- **redis**: Redis for caching and Celery broker
- **nginx**: Static file serving
- **proxy**: Nginx Proxy Manager for SSL/reverse proxy (ports 80, 81, 443)
- **grafana**: Monitoring dashboards

### Key Configuration Files

- `conf/local.py`: Django settings (extends Alliance Auth base settings)
- `conf/requirements.txt`: Additional Python packages for plugins
- `conf/celery.py`: Celery configuration
- `conf/urls.py`: URL routing overrides
- `custom.dockerfile`: Extends official AA image with custom requirements

### Installed Plugins

The deployment includes many Alliance Auth community plugins configured in `conf/local.py`:
- Discord integration and bot (aadiscordbot)
- Structure/timer tracking (structures, structuretimers)
- Member auditing (memberaudit, corptools)
- Fleet tracking (afat)
- Buyback programs, invoices, fittings, killtracker, and more

### Environment Variables

Configuration is managed via `.env` file. See `.env.example` for all available variables. Key settings include:
- Database credentials (AA_DB_*)
- ESI API credentials (ESI_SSO_*)
- Discord integration (DISCORD_*)
- Site URL configuration (PROTOCOL, AUTH_SUBDOMAIN, DOMAIN)
