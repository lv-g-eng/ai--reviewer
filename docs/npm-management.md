# NPM Management Guide

**Last Updated**: January 21, 2026

Complete guide for managing npm dependencies, cache, and security audits.

---

## 📋 Table of Contents

1. [Cache Management](#cache-management)
2. [Security Audits](#security-audits)
3. [Dependency Updates](#dependency-updates)
4. [CI/CD Integration](#cicd-integration)
5. [Troubleshooting](#troubleshooting)

---

## 🗂️ Cache Management

### Quick Commands

**Windows:**
```cmd
# Run cleanup
scripts\clean-npm-cache.bat

# Verify cleanup
scripts\verify-path-clean.bat
```

**Linux/macOS:**
```bash
# Make scripts executable
chmod +x scripts/clean-npm-cache.sh scripts/verify-path-clean.sh

# Run cleanup
./scripts/clean-npm-cache.sh

# Verify cleanup
./scripts/verify-path-clean.sh
```

### Manual Cache Cleanup

```bash
# Clean npm cache
npm cache clean --force

# Reset npm configurations
npm config delete cache
npm config delete prefix
npm config delete tmp

# Set clean cache path
npm config set cache "$PWD/.npm-cache"
export npm_config_cache="$PWD/.npm-cache"
```

### Environment Configuration

**Current Session:**
```bash
# Windows
set npm_config_cache=%CD%\.npm-cache

# Linux/macOS
export npm_config_cache="$PWD/.npm-cache"
```

**Permanent:**
```bash
# Windows: Add to System Environment Variables
# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
echo 'export npm_config_cache="$PWD/.npm-cache"' >> ~/.bashrc
```

---

## 🔐 Security Audits

### Running Audits

```bash
cd frontend

# Basic audit
npm audit

# Detailed JSON report
npm audit --json > audit-report.json

# Check specific severity levels
npm audit --audit-level=high
npm audit --audit-level=moderate
npm audit --audit-level=low
```

### Fixing Vulnerabilities

**Step 1: Automatic Fixes (Safe)**
```bash
# Respects package.json version constraints
npm audit fix
```

**Step 2: Review Remaining Issues**
```bash
# Check what's left
npm audit

# View dependency tree
npm ls --all
```

**Step 3: Manual Fixes**
```bash
# Update specific package
npm update <package-name>

# Install specific version
npm install <package-name>@<version>

# Force fix (use with caution)
npm audit fix --force
```

### Security Levels

| Level | Description | Command |
|-------|-------------|---------|
| Critical | Immediate action required | `npm audit --audit-level=critical` |
| High | Fix as soon as possible | `npm audit --audit-level=high` |
| Moderate | Fix in next release | `npm audit --audit-level=moderate` |
| Low | Fix when convenient | `npm audit --audit-level=low` |

---

## 📦 Dependency Updates

### Update Strategies

**Conservative (Recommended):**
```bash
# Update within semver range
npm update

# Check outdated packages
npm outdated
```

**Aggressive:**
```bash
# Update to latest versions
npm install <package>@latest

# Or use npm-check-updates
npx npm-check-updates -u
npm install
```

### Best Practices

✅ **DO:**
- Run `npm audit` regularly (weekly)
- Update dependencies monthly
- Review changelogs before major updates
- Test thoroughly after updates
- Commit `package-lock.json`

❌ **DON'T:**
- Ignore high/critical vulnerabilities
- Always use `--force` without review
- Update all packages at once
- Commit vulnerable dependencies

---

## 🔄 CI/CD Integration

### GitHub Actions - Audit Workflow

Create `.github/workflows/npm-audit.yml`:

```yaml
name: NPM Security Audit

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: "0 0 * * 0" # Weekly on Sunday

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Run npm audit
        run: cd frontend && npm audit --audit-level=moderate
        continue-on-error: true
      
      - name: Generate audit report
        run: cd frontend && npm audit --json > audit-report.json
      
      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: npm-audit-report
          path: frontend/audit-report.json
```

### Docker Integration

```dockerfile
# In your Dockerfile
FROM node:18-alpine

# Set clean cache path
ENV npm_config_cache=/app/.npm-cache

# Clean cache
RUN npm cache clean --force

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build
RUN npm run build
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: npm command not found**
```bash
# Solution: Install Node.js
# Download from: https://nodejs.org/
```

**Issue: Permission denied**
```bash
# Windows: Run as administrator
# Linux/macOS: Use sudo or fix permissions
sudo chown -R $USER ~/.npm
```

**Issue: Chinese characters in paths**
```bash
# Solution: Run cleanup script
scripts\clean-npm-cache.bat  # Windows
./scripts/clean-npm-cache.sh # Linux/macOS
```

**Issue: Peer dependency conflicts**
```bash
# Check what's requested
npm ls <package-name>

# Install compatible version
npm install <package-name>@<compatible-version>

# Or use --legacy-peer-deps
npm install --legacy-peer-deps
```

**Issue: Cache directory not writable**
```bash
# Check permissions
ls -la ~/.npm  # Linux/macOS
dir %APPDATA%\npm-cache  # Windows

# Fix permissions
chmod -R 755 ~/.npm  # Linux/macOS
```

### Verification Checklist

✅ npm cache path: English characters only  
✅ npm prefix path: English characters only  
✅ npm tmp path: English characters only  
✅ Environment variables: No Chinese characters  
✅ .npmrc file: No Chinese characters  
✅ npm commands: Work without errors  

---

## 📊 Automated Dependency Management

### Dependabot (GitHub)

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-team"
    labels:
      - "dependencies"
      - "npm"
```

### Renovate Bot

Create `renovate.json`:

```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    }
  ],
  "schedule": ["before 3am on Monday"],
  "timezone": "UTC"
}
```

---

## 📚 Additional Resources

- [npm Documentation](https://docs.npmjs.com/)
- [npm Audit Documentation](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Cache
npm cache clean --force
npm cache verify

# Audit
npm audit
npm audit fix
npm audit --json

# Updates
npm outdated
npm update
npm install <package>@latest

# Dependencies
npm ls --all
npm ls <package-name>
npm ci  # Clean install from lock file
```

### Script Locations

- Cleanup: `scripts/clean-npm-cache.{sh,bat}`
- Verification: `scripts/verify-path-clean.{sh,bat}`
- Documentation: `docs/npm-management.md` (this file)

---

**For more help, see [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)**
