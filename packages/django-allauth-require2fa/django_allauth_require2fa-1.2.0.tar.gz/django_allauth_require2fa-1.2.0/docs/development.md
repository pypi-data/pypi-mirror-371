# Development Guide

Complete guide for developing `django-allauth-require2fa` using modern Python tooling and best practices.

## 🚀 Quick Setup

### Prerequisites
- **Python 3.12+** (required)
- **UV package manager** (recommended)
- **Git** (for version control)

### One-Command Setup
```bash
# Clone and setup everything
git clone https://github.com/heysamtexas/django-allauth-require2fa.git
cd django-allauth-require2fa
make dev-setup

# Verify installation
make test
```

This single command:
- ✅ Installs UV if needed
- ✅ Sets up Python environment with dependencies
- ✅ Installs pre-commit hooks
- ✅ Verifies everything works

## 🛠️ Development Environment

### Tools Used (2025 Best Practices)

- **UV**: Lightning-fast Python package manager (150x faster than pip)
- **Ruff**: Rust-based linter and formatter (150x faster than flake8/black)
- **Bandit**: Security vulnerability scanner
- **MyPy**: Static type checking
- **Pre-commit**: Automated quality enforcement
- **Django**: Test framework integration

### Manual Setup (Alternative)

If you prefer manual control:

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Setup pre-commit hooks
uv run pre-commit install

# Verify setup
uv run python -m django test require2fa.tests --settings=require2fa.tests.settings
```

## 📁 Project Structure

```
django-allauth-require2fa/
├── require2fa/                    # Main package
│   ├── __init__.py               # Package initialization
│   ├── middleware.py             # Core 2FA enforcement middleware
│   ├── models.py                 # Django-Solo configuration model
│   ├── admin.py                  # Django admin interface
│   ├── apps.py                   # Django app configuration
│   ├── migrations/               # Database migrations
│   └── tests/                    # Comprehensive test suite
│       ├── settings.py           # Test Django settings
│       └── test_middleware.py    # 15 security tests
├── .github/                      # GitHub automation
│   ├── workflows/                # CI/CD pipelines
│   └── PULL_REQUEST_TEMPLATE.md  # PR guidance
├── docs/                         # Documentation
│   ├── releases.md               # Release process docs
│   └── development.md            # This file
├── pyproject.toml                # Package configuration
├── Makefile                      # Development commands
├── CONTRIBUTING.md               # Contributor guide
└── README.md                     # Package documentation
```

## 🔧 Development Commands

### Makefile Shortcuts (Recommended)

```bash
# Full development workflow
make all                     # Install deps + quality checks + tests

# Quality assurance
make quality                 # All quality checks (format, lint, security, types)
make format                  # Auto-format code with ruff
make lint                    # Check code style with ruff
make security               # Security scan with bandit
make mypy                   # Type checking with mypy

# Testing
make test                   # Run Django test suite
make test-verbose           # Run tests with detailed output

# Utilities
make clean                  # Remove generated files
make help                   # Show all available commands
```

### Manual Commands (UV)

```bash
# Development workflow
uv sync --dev                                    # Install/update dependencies
uv run --extra dev ruff format .                # Format code
uv run --extra dev ruff check .                 # Lint code
uv run --extra dev bandit -r require2fa/        # Security scan
uv run --extra dev mypy require2fa/             # Type checking

# Testing
uv run python -m django test require2fa.tests --settings=require2fa.tests.settings --verbosity=2

# Package management
uv add django>=4.2                              # Add runtime dependency
uv add --dev pytest                             # Add development dependency
uv build                                        # Build package for distribution
```

## 🧪 Testing Framework

### Test Suite Overview

The project includes **15 comprehensive security tests** covering:

1. **Integration Tests** (7 tests)
   - Middleware behavior with authenticated/unauthenticated users
   - URL exemption logic (static files, authentication flows)
   - Configuration toggle functionality

2. **Security Tests** (5 tests)
   - Path traversal protection
   - Malformed URL handling
   - Django configuration security

3. **Regression Tests** (3 tests)
   - Known vulnerability prevention
   - Breaking change detection

### Running Tests

```bash
# All tests
make test

# Verbose output with detailed logging
make test-verbose

# Specific test categories
uv run python -m django test require2fa.tests.SecurityRegressionTest
uv run python -m django test require2fa.tests.ConfigurationSecurityTest
uv run python -m django test require2fa.tests.Require2FAMiddlewareIntegrationTest

# Individual test methods
uv run python -m django test require2fa.tests.SecurityRegressionTest.test_accounts_namespace_no_longer_bypassed
```

### Test Settings

Tests use isolated Django settings (`require2fa/tests/settings.py`):
- Minimal Django configuration
- In-memory SQLite database
- Security-focused middleware stack
- Comprehensive logging for debugging

## 🔒 Security Development

### Security-Critical Guidelines

This middleware is **security-critical** infrastructure. Follow these guidelines:

#### Code Review Requirements
- **All middleware changes** require security review
- **URL resolution logic** needs extra scrutiny
- **Configuration handling** must prevent dangerous setups
- **Test coverage** must be maintained at 100%

#### Security Testing
```bash
# Run security-specific tests
uv run python -m django test require2fa.tests.SecurityRegressionTest
uv run python -m django test require2fa.tests.ConfigurationSecurityTest

# Security vulnerability scanning
make security
uv run --extra dev bandit -r require2fa/ --exclude require2fa/tests/
```

#### Common Security Pitfalls
1. **String-based URL matching** - Use Django's `resolve()` instead
2. **Hardcoded exemptions** - Use proper URL name resolution
3. **Configuration bypasses** - Validate Django settings safety
4. **Path traversal** - Test malformed URL handling

### Security Architecture

#### URL Resolution Strategy
```python
# ✅ Correct - uses Django URL dispatcher
try:
    resolved = resolve(request.path_info)
    if resolved.url_name in EXEMPT_URL_NAMES:
        return self.get_response(request)
except Resolver404:
    pass

# ❌ Wrong - vulnerable to path traversal
if request.path_info.startswith('/accounts/'):
    return self.get_response(request)
```

#### Configuration Validation
```python
# Prevent dangerous Django settings
static_url = getattr(settings, 'STATIC_URL', '/static/')
media_url = getattr(settings, 'MEDIA_URL', '/media/')

# Validate settings don't bypass security
if static_url == '/' or media_url == '/':
    logger.warning("Dangerous Django configuration detected")
```

## 📊 Code Quality

### Quality Tools Configuration

All tools configured in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "TCH", "DJ", "S"]
ignore = ["E501", "S101"]  # Line length handled by formatter, allow assert in tests

[tool.mypy]
python_version = "3.12"
plugins = ["mypy_django_plugin.main"]
ignore_missing_imports = true
exclude = ["require2fa/tests/", "require2fa/migrations/"]

[tool.bandit]
exclude_dirs = ["tests", "migrations"]
skips = ["B101", "B105", "B106"]  # Allow assert, hardcoded test secrets
```

### Pre-commit Hooks

Automatically enforced on every commit:
- **Ruff formatting** - Consistent code style
- **Ruff linting** - Code quality checks
- **Bandit security** - Security vulnerability scanning
- **MyPy typing** - Static type checking
- **Standard hooks** - Trailing whitespace, YAML validation, etc.

### Quality Standards

- **100% type coverage** - All functions have type hints
- **Security first** - Zero tolerance for security vulnerabilities
- **Performance optimized** - Use Rust-based tooling (Ruff)
- **Modern Python** - Python 3.12+ features encouraged

## 🔄 Development Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/my-improvement

# Work freely - any commit messages OK on branches
git commit -m "WIP: trying something"
git commit -m "still broken"
git commit -m "fix: finally working"

# Push to GitHub
git push origin feature/my-improvement
```

### Pull Request Process

1. **Create PR** with conventional commit title:
   ```
   feat: add runtime configuration for 2FA policies
   ```

2. **Automated checks** run:
   - Conventional commit validation
   - Full quality gate (lint, format, security, types)
   - Complete test suite (15 security tests)

3. **Review process**:
   - Security review for middleware changes
   - Code quality verification
   - Test coverage confirmation

4. **Merge to master**:
   - Triggers automated release process
   - Version bump based on PR title
   - PyPI publishing within 5 minutes

### Local Development Loop

```bash
# Make changes
vim require2fa/middleware.py

# Run quality checks
make quality

# Run tests
make test

# Commit and push
git add .
git commit -m "feat: add new authentication bypass"
git push origin feature/auth-bypass
```

## 🐛 Debugging

### Common Development Issues

#### Import Errors
```bash
# Ensure dependencies are installed
uv sync --dev

# Check Python path
uv run python -c "import require2fa; print(require2fa.__file__)"
```

#### Test Failures
```bash
# Run individual test with verbose output
uv run python -m django test require2fa.tests.test_middleware.Require2FAMiddlewareIntegrationTest.test_security_vulnerability_fixed --verbosity=2

# Check Django settings
uv run python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'require2fa.tests.settings')
import django
django.setup()
from django.conf import settings
print('INSTALLED_APPS:', settings.INSTALLED_APPS)
"
```

#### Quality Check Failures
```bash
# Format code automatically
make format

# Check what lint issues exist
uv run --extra dev ruff check . --diff

# See security issues
uv run --extra dev bandit -r require2fa/ -f screen

# Type checking details
uv run --extra dev mypy require2fa/ --show-error-codes
```

### Debugging Tools

```bash
# Django shell with test settings
uv run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'require2fa.tests.settings')
django.setup()
from require2fa.models import TwoFactorConfig
print('Config:', TwoFactorConfig.get_solo())
"

# Test middleware directly
uv run python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'require2fa.tests.settings')
django.setup()
from django.test import RequestFactory
from require2fa.middleware import Require2FAMiddleware

def dummy_response(request):
    return None

middleware = Require2FAMiddleware(dummy_response)
factory = RequestFactory()
request = factory.get('/')
result = middleware._is_static_request(request)
print('Is static:', result)
"
```

## 📦 Package Management

### Dependency Management

```bash
# Add runtime dependencies
uv add django>=4.2 django-allauth>=0.57.0

# Add development dependencies
uv add --dev ruff bandit mypy pytest

# Update dependencies
uv sync --upgrade

# Check for security vulnerabilities
uv run python -m pip_audit
```

### Building and Distribution

```bash
# Build package
uv build

# Check package contents
tar -tzf dist/django-allauth-require2fa-*.tar.gz
unzip -l dist/django_allauth_require2fa-*-py3-none-any.whl

# Install locally for testing
uv pip install -e .

# Test in fresh environment
uv run --isolated python -c "import require2fa; print('Import successful')"
```

## 🎯 Performance Optimization

### Development Performance

- **UV**: 150x faster than pip for dependency resolution
- **Ruff**: 150x faster than traditional Python linters
- **Parallel CI**: Quality checks run in parallel
- **Caching**: Aggressive caching in CI/CD pipeline

### Runtime Performance

- **Minimal overhead**: Middleware optimized for production
- **URL resolution caching**: Django's resolver is cached
- **Configuration caching**: Database queries minimized
- **Static file detection**: Fast path for static resources

---

**Next Steps**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines and [docs/releases.md](releases.md) for release process details.