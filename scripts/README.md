# Scripts Documentation

**Last Updated**: January 21, 2026

This directory contains utility scripts for project setup, maintenance, security, and operations.

---

## 📋 Table of Contents

1. [Setup Scripts](#setup-scripts)
2. [Maintenance Scripts](#maintenance-scripts)
3. [Security Scripts](#security-scripts)
4. [Utility Scripts](#utility-scripts)
5. [Usage Guidelines](#usage-guidelines)

---

## 🚀 Setup Scripts

### LLM Setup

**Files**: `setup-llm.bat`, `setup-llm.sh`

Sets up the local LLM environment with required models and dependencies.

**Usage:**
```bash
# Windows
scripts\setup-llm.bat

# Linux/macOS
chmod +x scripts/setup-llm.sh
./scripts/setup-llm.sh
```

**What it does:**
- Downloads required LLM models
- Installs Python dependencies
- Configures LLM service
- Verifies installation

**See also**: [docs/LLM_QUICK_START.md](../docs/LLM_QUICK_START.md)

---

### Development Environment Setup

**File**: `setup-dev.sh`

Sets up the complete development environment.

**Usage:**
```bash
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh
```

**What it does:**
- Installs system dependencies
- Sets up Python virtual environment
- Installs Node.js dependencies
- Configures databases
- Creates environment files

---

## 🧹 Maintenance Scripts

### NPM Cache Cleanup

**Files**: `clean-npm-cache.bat`, `clean-npm-cache.sh`

Cleans npm cache and removes problematic path configurations.

**Usage:**
```bash
# Windows
scripts\clean-npm-cache.bat

# Linux/macOS
chmod +x scripts/clean-npm-cache.sh
./scripts/clean-npm-cache.sh
```

**What it does:**
- Deletes `node_modules` and `package-lock.json`
- Runs `npm cache clean --force`
- Removes Chinese character paths
- Configures clean cache path
- Verifies cleanup

**See also**: [docs/npm-management.md](../docs/npm-management.md)

---

### Path Verification

**Files**: `verify-path-clean.bat`, `verify-path-clean.sh`

Verifies that all paths are clean and CI/CD ready.

**Usage:**
```bash
# Windows
scripts\verify-path-clean.bat

# Linux/macOS
chmod +x scripts/verify-path-clean.sh
./scripts/verify-path-clean.sh
```

**What it checks:**
- npm configurations
- Environment variables
- Project files
- npm command functionality

---

### Frontend Build Fix

**File**: `fix_frontend_build.bat`

Fixes common frontend build issues.

**Usage:**
```bash
scripts\fix_frontend_build.bat
```

**What it does:**
- Cleans `.next` directory
- Removes `node_modules`
- Reinstalls dependencies
- Runs build verification

---

### Project Organization

**File**: `organize_project.py`

Organizes and archives redundant project files.

**Usage:**
```bash
python scripts/organize_project.py
```

**What it does:**
- Identifies redundant files
- Creates dated archive directory
- Moves files to appropriate categories
- Generates archive index
- Updates project index

---

### Documentation Consolidation

**File**: `consolidate_docs.py`

Consolidates and organizes documentation files.

**Usage:**
```bash
python scripts/consolidate_docs.py
```

**What it does:**
- Identifies duplicate documentation
- Merges similar content
- Updates cross-references
- Archives old versions

---

## 🔐 Security Scripts

### Git Secrets Removal

**File**: `remove_git_secrets.sh`

Removes secrets from git history (use with extreme caution).

**Usage:**
```bash
chmod +x scripts/remove_git_secrets.sh
./scripts/remove_git_secrets.sh
```

**⚠️ Warning**: This rewrites git history. Backup your repository first!

**What it does:**
- Scans git history for secrets
- Removes identified secrets
- Rewrites git history
- Updates all branches

**See also**: [docs/SECRETS_CLEANUP_GUIDE.md](../docs/SECRETS_CLEANUP_GUIDE.md)

---

### Security Compliance Report

**File**: `security_compliance_report.py`

Generates comprehensive security compliance reports.

**Usage:**
```bash
python scripts/security_compliance_report.py
```

**What it generates:**
- Dependency vulnerability report
- Code security analysis
- Compliance checklist
- Remediation recommendations

**See also**: [docs/SECURITY.md](../docs/SECURITY.md)

---

## 🛠️ Utility Scripts

### AI Self-Healing

**File**: `ai_self_healing.py`

AI-powered automated error detection and fixing.

**Usage:**
```bash
python scripts/ai_self_healing.py
```

**What it does:**
- Scans codebase for errors
- Uses AI to suggest fixes
- Applies fixes automatically (with confirmation)
- Generates fix report

**See also**: [docs/AI_SELF_HEALING_GUIDE.md](../docs/AI_SELF_HEALING_GUIDE.md)

---

### Code Duplication Detection

**File**: `detect_code_duplication.py`

Detects duplicate code across the project.

**Usage:**
```bash
python scripts/detect_code_duplication.py
```

**What it reports:**
- Duplicate code blocks
- Similarity percentage
- Refactoring suggestions
- Impact analysis

---

### Requirements Generation

**File**: `generate_requirements.py`

Generates Python requirements files from imports.

**Usage:**
```bash
python scripts/generate_requirements.py
```

**What it does:**
- Scans Python files for imports
- Identifies required packages
- Generates requirements.txt
- Pins versions

---

### File Path Scanner

**File**: `scan_file_paths.py`

Scans for problematic file paths.

**Usage:**
```bash
python scripts/scan_file_paths.py
```

**What it checks:**
- Non-ASCII characters
- Path length issues
- Special characters
- Case sensitivity problems

---

### LLM Integration Test

**File**: `test-llm-integration.py`

Tests LLM service integration.

**Usage:**
```bash
python scripts/test-llm-integration.py
```

**What it tests:**
- LLM service connectivity
- Model loading
- Inference functionality
- Response quality

---

### Optimization Validation

**File**: `validate_optimization.py`

Validates code optimizations.

**Usage:**
```bash
python scripts/validate_optimization.py
```

**What it validates:**
- Performance improvements
- Memory usage
- Code quality metrics
- Regression tests

---

### Frontend Environment Verification

**Files**: `verify-frontend-env.sh`, `verify-frontend-env-enhanced.sh`

Verifies frontend environment configuration.

**Usage:**
```bash
chmod +x scripts/verify-frontend-env.sh
./scripts/verify-frontend-env.sh

# Enhanced version with more checks
./scripts/verify-frontend-env-enhanced.sh
```

**What it checks:**
- Environment variables
- Node.js version
- npm configuration
- Build requirements

---

## 📖 Usage Guidelines

### General Best Practices

1. **Always backup** before running destructive scripts
2. **Read the script** before executing
3. **Check permissions** on Linux/macOS
4. **Run from project root** unless specified otherwise
5. **Review output** for errors or warnings

### Script Permissions (Linux/macOS)

```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Or individually
chmod +x scripts/setup-llm.sh
```

### Windows Execution Policy

If you encounter execution policy errors:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Running Python Scripts

Ensure you're in the correct environment:

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Then run script
python scripts/script_name.py
```

---

## 🔄 Script Dependencies

### System Requirements

**All Scripts:**
- Git
- Bash (Linux/macOS) or PowerShell (Windows)

**Python Scripts:**
- Python 3.11+
- pip
- Virtual environment (recommended)

**Node.js Scripts:**
- Node.js 18+
- npm 9+

### Python Package Dependencies

Most Python scripts require:
```bash
pip install -r backend/requirements.txt
```

---

## 🐛 Troubleshooting

### Common Issues

**Script not found:**
```bash
# Ensure you're in project root
cd /path/to/project
ls scripts/  # Should list all scripts
```

**Permission denied (Linux/macOS):**
```bash
chmod +x scripts/script-name.sh
```

**Python module not found:**
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r backend/requirements.txt
```

**npm command not found:**
```bash
# Install Node.js from nodejs.org
# Verify installation
node --version
npm --version
```

---

## 📊 Script Categories Summary

| Category | Scripts | Purpose |
|----------|---------|---------|
| Setup | 2 | Environment initialization |
| Maintenance | 6 | Project upkeep |
| Security | 2 | Security operations |
| Utility | 8 | Various tools |
| **Total** | **18** | **All purposes** |

---

## 📞 Getting Help

If you encounter issues with any script:

1. Check this README
2. Review script-specific documentation
3. Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
4. Review script source code
5. Ask in team chat
6. Create GitHub issue

---

## 🔗 Related Documentation

- [Quick Reference](../QUICK_REFERENCE.md) - Common commands
- [NPM Management](../docs/npm-management.md) - NPM operations
- [Security Guide](../docs/SECURITY.md) - Security practices
- [LLM Quick Start](../docs/LLM_QUICK_START.md) - LLM setup

---

**For more information, see the main [README.md](../README.md)**
