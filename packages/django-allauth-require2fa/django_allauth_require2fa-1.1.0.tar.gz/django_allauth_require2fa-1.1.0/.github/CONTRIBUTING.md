# Contributing to django-allauth-require2fa

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start

1. **Fork and clone** the repository
2. **Set up development environment**:
   ```bash
   cd django-allauth-require2fa
   make dev-setup  # Installs deps + pre-commit hooks
   ```
3. **Run tests** to verify setup: `make test`
4. **Make your changes** following our guidelines below
5. **Submit a Pull Request**

## 📝 Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for **automated versioning** and **changelog generation**.

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature (triggers minor version bump)
- **fix**: Bug fix (triggers patch version bump)
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI/CD changes  
- **chore**: Maintenance tasks

### Examples
```bash
feat: add site-wide 2FA enforcement middleware
fix: resolve path traversal vulnerability in URL matching
docs: update installation instructions for Django 5.1
test: add security tests for malformed URL handling
chore: upgrade ruff to latest version
```

### Breaking Changes
For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:
```bash
feat!: require Python 3.12+ for enhanced security features
# or
feat: migrate to new configuration format

BREAKING CHANGE: The old REQUIRE_2FA setting is no longer supported.
Use the Django admin interface to configure 2FA enforcement.
```

## 🧪 Development Workflow

### Available Commands (Makefile)
```bash
# Development setup
make dev-setup          # One-time setup: deps + pre-commit hooks

# Testing  
make test               # Run Django test suite
make mypy               # Type checking

# Code Quality
make format             # Auto-format with ruff
make lint               # Check code style with ruff
make security           # Security scan with bandit
make quality            # Run all quality checks

# Complete workflow
make all                # install + quality + test
```

### Manual Commands (Alternative)
```bash
# Setup
uv sync --dev
uv run pre-commit install

# Testing
uv run python -m django test require2fa.tests --settings=require2fa.tests.settings

# Quality
uv run ruff format .
uv run ruff check .
uv run bandit -r require2fa/
uv run mypy require2fa/
```

## 🔒 Security Guidelines

This is a **security-critical middleware**. Special care is required:

### Required for Security Changes
- **Comprehensive testing** - Add tests covering edge cases
- **Security review** - Changes to middleware logic need careful review  
- **Documentation** - Update security considerations in README
- **Vulnerability disclosure** - Follow responsible disclosure for security issues

### Testing Security Changes
- Run the **full test suite**: `make test`
- Add **regression tests** for any vulnerabilities fixed
- Test with **malformed inputs** and **edge cases**
- Verify **URL resolution** works correctly with various Django configurations

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] **Tests pass**: `make test`
- [ ] **Quality checks pass**: `make quality`  
- [ ] **Pre-commit hooks** are installed and passing
- [ ] **Conventional commit** format in PR title
- [ ] **Description** explains the change and why it's needed

### PR Title Format
Your PR title must follow conventional commits format:
```
feat: add support for custom 2FA redirect URLs
fix: resolve middleware ordering issue with AllAuth
docs: improve installation guide with troubleshooting
```

### Security-Related PRs
For security fixes:
- Mark PR as **draft** initially for security review
- Include **detailed description** of vulnerability (if applicable)
- Add **test cases** demonstrating the fix
- Update **security documentation** if needed

## 🤖 Automated Processes

### Releases
- **Automatic versioning** based on commit messages
- **Semantic versioning**: major.minor.patch
- **Automatic changelogs** generated from commits
- **PyPI publishing** triggered by semantic release

### Quality Assurance
- **Pre-commit hooks** run ruff, bandit, and mypy
- **CI pipeline** validates all code changes
- **Security scanning** with CodeQL and Bandit
- **Dependency updates** via Dependabot

## 🆘 Getting Help

- **Questions**: Open a [Discussion](https://github.com/heysamtexas/django-allauth-require2fa/discussions)
- **Bug reports**: Open an [Issue](https://github.com/heysamtexas/django-allauth-require2fa/issues)
- **Security issues**: Email security@[domain] (see SECURITY.md)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Django applications more secure! 🔐**