# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of django-allauth-require2fa package
- Site-wide 2FA enforcement middleware
- Runtime configuration via Django admin
- Security-hardened URL resolution
- Comprehensive test suite with 15 security tests
- Support for Python 3.12+
- Support for Django 4.2+
- Modern packaging with pyproject.toml and hatchling
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline
- Automated PyPI releases

### Security
- Fixed path traversal vulnerability from django-allauth PR #3710
- Proper Django URL resolution instead of string matching
- Configuration validation to prevent dangerous settings
- Security logging for audit trails
- Protection against admin bypass attempts

### Changed
- Extracted from internal Django module to standalone package
- Updated to use django-solo for singleton configuration
- Modernized codebase for Python 3.12+ with type hints
- Comprehensive security testing approach

## [0.1.0] - 2024-12-XX

### Added
- Initial package structure
- Core middleware implementation
- Django admin integration
- Database migrations
- Basic test suite

[Unreleased]: https://github.com/heysamtexas/django-allauth-require2fa/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/heysamtexas/django-allauth-require2fa/releases/tag/v0.1.0
