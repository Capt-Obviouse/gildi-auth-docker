# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Reduce Celery worker replicas from 2 to 1 to lower memory usage
- Add Redis memory limit (256MB) and LRU eviction policy to prevent unbounded cache growth
- Remove local MariaDB in favor of external RDS instance
- Update Grafana to connect to RDS instead of local MariaDB

### Fixed
- Fix Redis health check - use `REDIS_URL` setting instead of nested `HEALTH_CHECK` dict
- Fix `AA_LOG_LEVEL` to actually control all loggers (set root logger and console handler)

## [0.2.1] - 2025-12-05

### Added
- `AA_LOG_LEVEL` environment variable to control logging verbosity (defaults to `INFO`)

### Changed
- Default log level changed from `DEBUG` to `INFO` to reduce log spam

### Fixed
- Updated nginx config to use new `aa_gunicorn` service name

## [0.1.0] - 2025-12-05

### Added
- CLAUDE.md for AI assistant context
- Comprehensive README with setup instructions, common commands, and troubleshooting
- Documentation for automatic package updates via `scripts/update_from_packagemonitor.py`
- Guidelines for when to rebuild vs restart containers

### Changed
- Renamed all Docker services from `allianceauth_*` to `aa_*` for brevity
  - `allianceauth_gunicorn` → `aa_gunicorn`
  - `allianceauth_worker` → `aa_worker`
  - `allianceauth_beat` → `aa_beat`
  - `allianceauth_discordbot` → `aa_discordbot`
  - `allianceauth_cli` → `aa_cli`
- Simplified docker compose commands by removing redundant `--env-file=.env` flag
