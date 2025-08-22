## 📝 Pull Request Title (Important!)

**Your PR title determines the version bump and release type. Use conventional commit format:**

```
<type>[optional scope]: <description>
```

**Examples:**
- `feat: add runtime configuration for 2FA policies` (→ Minor release: 1.0.0 → 1.1.0)
- `fix: resolve path traversal vulnerability` (→ Patch release: 1.0.0 → 1.0.1)
- `docs: add comprehensive release documentation` (→ No release)

## 🎯 Description

### What does this PR do?
<!-- Describe the changes and why they're needed -->

### What type of change is this?
<!-- Check one -->
- [ ] 🆕 **feat**: New feature (minor version bump)
- [ ] 🐛 **fix**: Bug fix (patch version bump)
- [ ] 📚 **docs**: Documentation changes (no release)
- [ ] 🎨 **style**: Code style changes (no release)
- [ ] ♻️ **refactor**: Code refactoring (patch version bump)
- [ ] ⚡ **perf**: Performance improvements (patch version bump)
- [ ] ✅ **test**: Adding/updating tests (no release)
- [ ] 🔧 **chore**: Maintenance tasks (no release)

## 🔒 Security Checklist

<!-- Required for all changes to security-critical middleware -->
- [ ] **Security impact assessed** - No new attack vectors introduced
- [ ] **URL resolution reviewed** - No string-based path matching added
- [ ] **Test coverage maintained** - All 15 security tests still pass
- [ ] **Configuration safety** - No dangerous Django settings enabled

## ✅ Quality Checklist

<!-- These are automatically checked by CI, but good to verify locally -->
- [ ] **Code formatted** - `make format` runs clean
- [ ] **Linting passes** - `make lint` shows no issues
- [ ] **Security scan clean** - `make security` passes
- [ ] **Type checking** - `make mypy` passes with no errors
- [ ] **Tests pass** - `make test` completes successfully
- [ ] **Full workflow** - `make all` completes without errors

## 🚀 Release Impact

### Version Impact
<!-- Based on your PR title type -->
- [ ] This will trigger a **minor release** (new features)
- [ ] This will trigger a **patch release** (bug fixes, improvements)
- [ ] This will **not trigger a release** (docs, chore, etc.)

### Breaking Changes
- [ ] **No breaking changes** - Existing users unaffected
- [ ] **Breaking changes present** - Migration guide provided
- [ ] **Configuration changes** - Admin interface changes documented

## 🧪 Testing

### How was this tested?
<!-- Describe your testing approach -->
- [ ] **Unit tests added/updated** for new functionality
- [ ] **Security tests verify** no regressions
- [ ] **Manual testing completed** with Django test project
- [ ] **Edge cases considered** (malformed URLs, edge configurations)

### Test Results
```bash
# Paste output of: make all
```

## 📋 Additional Context

### Related Issues
<!-- Link any related issues -->
- Fixes #(issue number)
- Related to #(issue number)

### Documentation Updates
- [ ] **README updated** if user-facing changes
- [ ] **CHANGELOG.md entry** will be auto-generated from PR title
- [ ] **API documentation** updated if applicable

### Deployment Notes
<!-- Any special considerations for deployment -->
- [ ] **Migration required** - `python manage.py migrate require2fa`
- [ ] **Configuration update needed** - Admin interface changes
- [ ] **No deployment actions required**

---

## 🎯 Reviewer Guidelines

### For Reviewers
- **Security Focus**: This is security-critical middleware - extra scrutiny required
- **Test Coverage**: Verify security test suite still provides comprehensive coverage
- **Breaking Changes**: Ensure backward compatibility or clear migration path
- **Release Impact**: Confirm PR title accurately reflects the change scope

### Automated Checks
The following will be automatically verified:
- ✅ **Conventional commit format** in PR title
- ✅ **All quality gates pass** (lint, format, security, types)
- ✅ **Complete test suite passes** (15 security tests + functionality)
- ✅ **No security vulnerabilities** detected

---

**Remember**: Your PR title determines the release! Use conventional commit format even if individual commits on your branch are messy.