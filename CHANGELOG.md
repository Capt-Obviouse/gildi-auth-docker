# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
