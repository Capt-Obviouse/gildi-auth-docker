# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.9] - 2025-12-20

### Changed
- Reduce gunicorn workers from 3 to 2 to lower memory usage
- Tune MariaDB for lower memory footprint:
  - Disable performance_schema (saves ~400MB)
  - Reduce per-connection buffer sizes
  - Reduce InnoDB log buffer to 8MB

## [0.2.8] - 2025-12-20

### Added
- Reauth reminder Discord bot cog for monthly director/CEO ESI token reminders
  - Sends monthly reminder to a configured Discord channel
  - Two buttons: "Corp Audit Tokens" (`/audit/r/corp`) and "Structure Owners" (`/structures/`)
  - Configurable: channel ID, role ping, day of month, and hour (UTC)
  - Admin test command `!testreauth` to preview the message
  - Environment variables: `REAUTH_REMINDER_CHANNEL_ID`, `REAUTH_REMINDER_ROLE_ID`, `REAUTH_REMINDER_DAY`, `REAUTH_REMINDER_HOUR`

## [0.2.7] - 2025-12-19

### Fixed
- Increase Celery worker memory health check threshold from 500MB to 700MB to prevent frequent restarts causing brief outages

## [0.2.6] - 2025-12-12

### Added
- S3 backup script for MariaDB (`scripts/backup-db.sh`) with configurable retention

### Changed
- Reduce Celery worker replicas from 2 to 1 to lower memory usage
- Add Redis memory limit (256MB) and LRU eviction policy to prevent unbounded cache growth
- Revert to local MariaDB container (from RDS) for cost savings

### Fixed
- Fix Redis health check - use `REDIS_URL` setting instead of nested `HEALTH_CHECK` dict
- Fix `AA_LOG_LEVEL` to actually control all loggers (set root logger and console handler)
- Fix backup script to load env vars before using them

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
