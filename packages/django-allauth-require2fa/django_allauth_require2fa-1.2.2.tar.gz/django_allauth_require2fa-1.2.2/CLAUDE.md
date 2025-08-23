# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `django-allauth-require2fa`, a standalone PyPI package that provides site-wide Two-Factor Authentication (2FA) enforcement middleware for Django applications. Originally extracted from a Django module, this repo is designed to be a fully installable package for Django projects using django-allauth.

### Key Purpose
- Enforces 2FA for all authenticated users across entire Django applications
- Provides runtime configuration via Django admin (no code changes needed)
- Fixes security vulnerabilities found in rejected django-allauth PR #3710
- Fills the gap left by django-allauth, which provides 2FA functionality but explicitly does not include site-wide enforcement

### Package Status
This package is designed for distribution via PyPI and follows modern Python packaging standards:
- Targets Python 3.12+ with latest syntax and best practices
- Uses modern tooling: uv, ruff, bandit, pre-commit
- Automated CI/CD with GitHub Actions for testing and PyPI releases

## Development Workflow

### Prerequisites
This project uses modern Python tooling requiring Python 3.12+:
```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### Development Commands (Makefile)

The project includes a Makefile for convenient development tasks:

```bash
# Development setup (one-time)
make dev-setup                        # Install deps + pre-commit hooks

# Testing
make test                              # Run Django tests
make mypy                              # Run type checking

# Code Quality
make format                            # Auto-format with ruff
make lint                              # Check code with ruff  
make security                          # Run bandit security scan
make quality                           # Run all quality checks

# Workflows
make all                               # Full workflow (install + quality + test)
make clean                             # Clean generated files
make help                              # Show all available commands
```

### Manual Commands (if needed)
```bash
# Testing
uv run python -m django test require2fa.tests --settings=require2fa.tests.settings --verbosity=2

# Code Quality  
uv run ruff check .                    # Check for issues
uv run ruff format .                   # Auto-format code
uv run bandit -r require2fa/           # Security checks
uv run mypy require2fa/                # Type checking

# Pre-commit hooks
uv run pre-commit install             # Install hooks
uv run pre-commit run --all-files     # Run all hooks manually
```

The test suite includes 15 comprehensive security tests covering:
- URL resolution edge cases  
- Malformed URL handling
- Static file exemptions
- Admin protection
- Configuration security
- Regression tests for known vulnerabilities

### Package Management
```bash
# Add dependencies
uv add django-allauth django-solo

# Add development dependencies  
uv add --dev pytest pytest-django ruff bandit pre-commit

# Build package
uv build

# Install locally for testing
uv pip install -e .
```

## Architecture

### Core Components

1. **Middleware (`middleware.py`)**: 
   - `Require2FAMiddleware` - The main enforcement engine
   - Uses proper Django URL resolution (not vulnerable string matching)
   - Supports both sync and async Django applications
   - Security-critical component with extensive logging

2. **Models (`models.py`)**:
   - `TwoFactorConfig` - Django-Solo singleton model for runtime configuration
   - Controls site-wide 2FA enforcement via admin interface

3. **Admin (`admin.py`)**:
   - `TwoFactorConfigAdmin` - Admin interface for toggling 2FA enforcement
   - Prevents deletion of singleton configuration

### Security Architecture

**URL Resolution Strategy**: Uses Django's `resolve()` function instead of string prefix matching to prevent path traversal vulnerabilities.

**Exempt URLs**: The middleware exempts specific django-allauth URL names:
- Authentication flows: `account_login`, `account_logout`, `account_reauthenticate`
- Email management: `account_email`, `account_confirm_email`
- Password reset flows
- MFA setup/management: `mfa_activate_totp`, `mfa_*_recovery_codes`

**Static File Handling**: Automatically detects and exempts `STATIC_URL` and `MEDIA_URL` paths, with security protection against dangerous root path configurations.

**Configuration Security**: Validates Django settings to prevent STATIC_URL or MEDIA_URL from being set to "/" which would bypass all 2FA enforcement.

### Integration Points

- **Django-Allauth**: Relies on `allauth.mfa.adapter.get_adapter()` to check if users have 2FA enabled
- **Django-Solo**: Uses singleton pattern for runtime configuration without restarts
- **Django Admin**: Provides web interface for 2FA policy management

### Migration Strategy

The app includes data migrations to handle configuration upgrades:
- `0001_initial.py`: Creates the TwoFactorConfig model
- `0002_copy_2fa_setting.py`: Migrates from any existing 2FA settings

### Security Considerations

1. **Path Traversal Protection**: Fixed vulnerability where `/accounts/../admin/` could bypass 2FA
2. **URL Resolution**: Uses Django's URL dispatcher, not string matching
3. **Configuration Validation**: Prevents dangerous Django settings that would bypass security
4. **Comprehensive Testing**: 15 security-focused tests ensure no regressions
5. **Security Logging**: Uses dedicated `security.2fa` logger for audit trails

### Code Patterns

- All security-critical code includes detailed comments explaining vulnerabilities
- Extensive use of subTest() in tests for clear failure reporting
- Type hints throughout for maintainability
- Django's `sync_and_async_middleware` decorator for ASGI/WSGI compatibility

## Package Release Process

### Version Management
This package uses semantic versioning and automated releases:
```bash
# Version is managed in pyproject.toml and __init__.py
# GitHub Actions automatically:
# 1. Runs tests and quality checks on PR
# 2. Builds and releases to PyPI on tagged releases
# 3. Creates GitHub releases with changelog
```

### Release Workflow
1. **Development**: Work on feature branches, use pre-commit hooks
2. **Testing**: All tests must pass, ruff/bandit checks must be clean
3. **Version Bump**: Update version in `pyproject.toml` and `require2fa/__init__.py`
4. **Tag Release**: Create Git tag (e.g., `v1.0.0`) to trigger PyPI release
5. **GitHub Actions**: Automatically builds, tests, and publishes to PyPI

### CI/CD Pipeline
GitHub Actions workflow includes:
- **Test Matrix**: Multiple Python versions (3.12+) and Django versions
- **Code Quality**: ruff linting/formatting, bandit security scanning
- **Testing**: Full test suite with coverage reporting
- **Release**: Automated PyPI publishing on tagged releases
- **Security**: Dependency vulnerability scanning

### Installation from PyPI
```bash
# Standard installation
pip install django-allauth-require2fa

# With uv (recommended)
uv add django-allauth-require2fa

# Development installation
pip install -e .
```

## Django Integration

### Installation Steps
1. Install package: `uv add django-allauth-require2fa`
2. Add to `INSTALLED_APPS`: `'require2fa'`
3. Add middleware: `'require2fa.middleware.Require2FAMiddleware'`
4. Run migrations: `python manage.py migrate require2fa`
5. Configure in Django Admin → Two-Factor Authentication Configuration

### Dependencies
- **Django**: 4.2+ (LTS versions)
- **django-allauth**: For MFA functionality integration
- **django-solo**: For singleton configuration model
- **Python**: 3.12+ for modern syntax and performance

## Important Notes

- This is a **security-critical** middleware - all changes require security review
- Package follows Django best practices for installable apps
- Never modify exempt URL logic without understanding security implications
- Always run full test suite (`uv run pytest`) when making changes to middleware logic
- Use pre-commit hooks to ensure code quality before commits
- Target Python 3.12+ and use modern Python features (match statements, type hints, etc.)