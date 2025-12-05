# Gildi Alliance Auth

Docker-based deployment of [Alliance Auth](https://allianceauth.org/) for EVE Online corporation/alliance management.

## Initial Setup

1. Run the setup script to generate your `.env` file with secure passwords:
   ```bash
   ./scripts/prepare-env.sh
   ```

2. Build and start all containers:
   ```bash
   docker compose up -d --build
   ```

3. Run initial database migrations:
   ```bash
   docker compose run --rm aa_cli migrate
   docker compose run --rm aa_cli collectstatic --noinput
   ```

4. Create a superuser:
   ```bash
   docker compose run --rm aa_cli createsuperuser
   ```

## Common Commands

### Start/Stop Services

```bash
# Start all containers
docker compose up -d

# Stop all containers
docker compose down

# Restart a specific service
docker compose restart <service_name>

# View logs
docker compose logs -f <service_name>
```

### Django Management

Use the `aa_cli` container for running management commands:

```bash
# Run any manage.py command
docker compose run --rm aa_cli <command>

# Open Django shell
docker compose run --rm aa_cli shell_plus

# Examples
docker compose run --rm aa_cli migrate
docker compose run --rm aa_cli collectstatic --noinput
```

## When to Build vs Restart

### Restart Only (no rebuild needed)

Use `docker compose restart` or `docker compose up -d` when:
- Changing `.env` values (environment variables)
- Modifying `conf/local.py` (Django settings)
- Modifying `conf/celery.py` or `conf/urls.py`
- Updating files in the `templates/` directory

### Rebuild Required

Use `docker compose up -d --build` when:
- Adding/updating packages in `conf/requirements.txt`
- Modifying `custom.dockerfile` or `Dockerfile`
- Changing the `AA_DOCKER_TAG` version in `.env`

After rebuilding for package changes, run migrations:
```bash
docker compose run --rm aa_cli migrate
docker compose run --rm aa_cli collectstatic --noinput
```

## Upgrading Alliance Auth

1. Update `AA_DOCKER_TAG` in `.env` to the new version

2. Pull and rebuild:
   ```bash
   docker compose pull
   docker compose up -d --build
   ```

3. Run upgrade commands:
   ```bash
   docker compose run --rm aa_cli migrate
   docker compose run --rm aa_cli collectstatic --noinput
   ```

## Updating Packages

### Automatic Update (via Package Monitor)

If you have the `package_monitor` app installed and configured, use the helper script to automatically update packages that have available updates:

```bash
python scripts/update_from_packagemonitor.py
```

This script will:
1. Query Package Monitor for available updates
2. Update matching packages in `conf/requirements.txt`
3. Rebuild the Docker images
4. Restart all services
5. Run migrations and collectstatic

### Manual Update

1. Edit `conf/requirements.txt` with new package versions

2. Rebuild containers:
   ```bash
   docker compose up -d --build
   ```

3. Run migrations if the package requires them:
   ```bash
   docker compose run --rm aa_cli migrate
   ```

## Services

| Service | Description | Port |
|---------|-------------|------|
| aa_gunicorn | Main web application | 8000 |
| aa_worker | Celery background workers (x2) | - |
| aa_beat | Celery task scheduler | - |
| aa_discordbot | Discord bot | - |
| aa_cli | CLI for running manage.py commands | - |
| auth_mysql | MariaDB database | 3306 (internal) |
| redis | Cache and message broker | 6379 (internal) |
| nginx | Static file server | - |
| proxy | Nginx Proxy Manager | 80, 81, 443 |
| grafana | Monitoring dashboards | - |

## Troubleshooting

### Check container status
```bash
docker compose ps
```

### View container logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f aa_gunicorn
```

### Restart unhealthy workers
```bash
docker compose restart aa_worker
```

### Database issues
```bash
# Check database connectivity
docker compose run --rm aa_cli dbshell
```
