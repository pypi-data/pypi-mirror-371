# Contributing to django-allauth-require2fa

Thank you for your interest in contributing! This project uses modern development workflows with automated quality gates and releases.

## 🚀 Quick Start

```bash
# Clone and setup (one command!)
git clone https://github.com/heysamtexas/django-allauth-require2fa.git
cd django-allauth-require2fa
make dev-setup

# Verify setup
make test
```

## 📝 Commit Message Format (Important!)

This project uses **automated releases** based on commit messages. Your commit messages determine if and how new versions are published to PyPI.

### Conventional Commits Required

Use this format: `<type>[optional scope]: <description>`

**Examples:**
```bash
feat: add user authentication bypass option
fix: resolve URL resolution vulnerability  
docs: update installation instructions
chore: update dependencies
```

### Release Impact

Your commit type determines the release:

| Type | Version Bump | Example |
|------|-------------|---------|
| `feat:` | **Minor** (1.0.0 → 1.1.0) | New features |
| `fix:`, `perf:`, `refactor:` | **Patch** (1.0.0 → 1.0.1) | Bug fixes, improvements |
| `docs:`, `chore:`, `ci:` | **No release** | Documentation, maintenance |

### Valid Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding/updating tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks
- **revert**: Revert previous commit

## 🔄 Development Workflow

### 1. Branch Strategy
```bash
# Create feature branch (any name is fine)
git checkout -b feature/my-improvement

# Work freely - commit messages can be anything on branches
git commit -m "WIP: trying stuff"
git commit -m "broken but saving work"
git commit -m "fix: resolve the actual issue"
```

### 2. Development Commands
```bash
# Full workflow (recommended)
make all                     # Install + quality + test

# Individual commands
make test                    # Run Django test suite
make quality                 # All quality checks
make format                  # Auto-format code
make lint                    # Check code style
make security               # Security scan
make mypy                   # Type checking
```

### 3. Pull Request Process
```bash
# When ready, create PR with conventional title
# PR title determines versioning (not individual commits)
```

**PR Title Examples:**
- `feat: add runtime configuration for 2FA policies`
- `fix: resolve path traversal vulnerability in URL matching`
- `docs: add comprehensive release documentation`

## 🔒 Security Requirements

This is a **security-critical** middleware. Extra care required for:

### Code Changes
- **Security review required** for all middleware modifications
- **Comprehensive testing** - maintain the 15-test security suite
- **Vulnerability analysis** - consider attack vectors
- **Backward compatibility** - security fixes shouldn't break existing setups

### Testing Requirements
```bash
# All tests must pass
make test

# Security tests are comprehensive
python -m django test require2fa.tests.SecurityRegressionTest
python -m django test require2fa.tests.ConfigurationSecurityTest
```

## 📦 Release Process (Automated)

### How Releases Work

1. **PR Merged to Master** → Triggers automation
2. **Commit Analysis** → Determines if release needed
3. **Quality Gates** → Runs all tests and security checks
4. **Version Bump** → Based on conventional commit type
5. **GitHub Release** → Automatic with changelog
6. **PyPI Publishing** → OIDC trusted publishing
7. **Documentation Update** → Release notes with installation

### What You Need to Know

- **You don't manually create releases** - automation handles everything
- **PR titles matter** - they determine version bumps
- **Quality gates prevent bad releases** - broken code never reaches PyPI
- **Time to PyPI: ~5 minutes** from merge to published package

### Manual Release Testing (Optional)
```bash
# Preview what release would happen
uv run semantic-release version --print --no-commit --no-tag --no-push --no-vcs-release

# Manual trigger (if needed)
gh workflow run semantic-release.yml
```

## 🎯 Quality Standards

### Code Quality (Automated)
- **Ruff formatting** - Auto-formatted code (150x faster than black)
- **Ruff linting** - Style and best practice checks
- **Bandit security** - Security vulnerability scanning
- **MyPy typing** - Static type checking
- **Pre-commit hooks** - Automatic quality enforcement

### Testing Standards
- **15 security tests** - Comprehensive security coverage
- **URL resolution tests** - Edge cases and malformed inputs
- **Configuration tests** - Dangerous Django settings protection
- **Regression tests** - Known vulnerability prevention

### Security Standards
- **Vulnerability scanning** - Every release scanned
- **OIDC publishing** - No API keys, unhackable releases
- **Audit logging** - Security events logged
- **Path traversal protection** - Proper URL resolution

## 💡 Tips for Contributors

### Development Best Practices
```bash
# Use the Makefile - it's optimized
make all                     # Instead of manual commands

# Run security tests frequently
make test

# Format before committing
make format
```

### Conventional Commit Tips
- **Be descriptive**: `feat: add LDAP integration` vs `feat: add feature`
- **Use lowercase**: `fix: resolve bug` not `Fix: Resolve Bug`
- **No period**: `docs: update readme` not `docs: update readme.`
- **Present tense**: `add` not `added` or `adds`

### PR Guidelines
- **One feature per PR** - easier to review and release
- **Conventional title** - determines versioning
- **Clear description** - explain the why, not just the what
- **Security considerations** - mention any security implications

## 🔧 Architecture Knowledge

### Key Components
- **Middleware**: `require2fa.middleware.Require2FAMiddleware`
- **Models**: `require2fa.models.TwoFactorConfig` (Django-Solo singleton)
- **Admin**: Runtime configuration interface
- **Tests**: 15 comprehensive security tests

### Security Architecture
- **URL Resolution**: Uses Django's `resolve()` not string matching
- **Static File Detection**: Automatic STATIC_URL/MEDIA_URL exemption
- **Configuration Validation**: Prevents dangerous Django settings

## 📚 Additional Resources

- **Release Documentation**: [docs/releases.md](docs/releases.md)
- **Development Guide**: [docs/development.md](docs/development.md)  
- **Architecture Details**: [CLAUDE.md](CLAUDE.md)
- **Conventional Commits**: [conventionalcommits.org](https://www.conventionalcommits.org/)
- **Semantic Versioning**: [semver.org](https://semver.org/)

## 🤝 Getting Help

- **Issues**: [GitHub Issues](https://github.com/heysamtexas/django-allauth-require2fa/issues)
- **Discussions**: [GitHub Discussions](https://github.com/heysamtexas/django-allauth-require2fa/discussions)
- **Security**: Email security issues privately

---

**Remember**: Your PR title determines the version bump! Use conventional commit format in PR titles even if individual commits on your branch are messy.