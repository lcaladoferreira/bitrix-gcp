# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-15
### Added
- **ESLM Pipeline**: Robust Extract-Stage-Load-Merge pattern implementation.
- **Incremental Sync**: Automated watermark-based data extraction.
- **Full Sync Support**: Overrides for full backfills and date-specific extraction.
- **Audit Logging**: Pipeline metrics and status tracked in BigQuery.
- **Infrastructure as Code**: Modular Terraform setup for GCP resources.
- **Containerization**: Production Dockerfile and local development Compose setup.
- **CI/CD**: GitHub Actions workflow for automated validation.
- **Multi-entity Support**: Configurable schemas for Deals, Leads, Contacts, Companies, and Activities.
