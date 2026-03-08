# CI/CD Pipeline Documentation

This document describes the complete CI/CD pipeline setup for the frontend application.

## Overview

The CI/CD pipeline consists of four main workflows:

1. **CI Pipeline** - Automated testing and quality checks
2. **Build Pipeline** - Application build and artifact creation
3. **Deploy Pipeline** - Automated deployment to test/production
4. **Rollback Pipeline** - One-click rollback capability
5. **Lighthouse CI** - Performance auditing

## Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Lint and Test**: Runs on Node.js 18.x and 20.x
  - ESLint code quality checks
  - TypeScript type checking
  - Unit tests with Jest
  - Test coverage validation (80% threshold)
  - Coverage report upload to Codecov
  - PR comments with coverage details

**Requirements Validated:**
- ✅ Requirement 13.5: CI pipeline runs lint and unit tests
- ✅ Requirement 17.1: Automatic lint and test execution on commit

**Exit Criteria:**
- All linting checks pass
- All tests pass
- Test coverage ≥ 80%

---

### 2. Build Pipeline (`.github/workflows/build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- After successful CI pipeline completion

**Jobs:**
- **Build Application**:
  - Install dependencies
  - Create production environment configuration
  - Build Next.js application
  - Verify build output
  - Check build size
  - Create compressed build artifact
  - Upload artifacts to GitHub
  - Generate build metadata
  - Comment PR with build information

**Artifacts Created:**
- `frontend-build-{SHA}.tar.gz` - Compressed build output
- `build-metadata.json` - Build information and metadata

**Requirements Validated:**
- ✅ Requirement 17.2: Automatic build after tests pass

**Retention:**
- Build artifacts: 30 days
- Build metadata: 30 days

---

### 3. Deploy Pipeline (`.github/workflows/deploy.yml`)

**Triggers:**
- Manual workflow dispatch (for all environments)
- Automatic after successful build (test environment only)

**Environments:**
- **Test**: Auto-deploy on main branch builds
- **Production**: Manual deployment only

**Jobs:**

#### Deploy to Test
- Download build artifacts
- Extract build files
- Deploy to test environment
- Create deployment record
- Upload deployment record

#### Deploy to Production
- Download build artifacts and metadata
- Verify build is from main branch
- Backup current production deployment
- Deploy to production
- Run post-deployment health checks
- Create deployment record
- Create GitHub release
- Send notifications

**Requirements Validated:**
- ✅ Requirement 17.3: Auto-deploy to test environment
- ✅ Requirement 17.4: One-click production deployment
- ✅ Requirement 17.5: Rollback support (via backup creation)

**Deployment Records:**
- Test deployments: 90 days retention
- Production deployments: 365 days retention

---

### 4. Rollback Pipeline (`.github/workflows/rollback.yml`)

**Triggers:**
- Manual workflow dispatch only

**Inputs:**
- `environment`: Target environment (test/staging/production)
- `backup_id`: Backup identifier to restore
- `previous_sha`: Previous build SHA to rollback to

**Jobs:**
- **Rollback**:
  - Validate rollback inputs
  - Confirm rollback action (10 second delay)
  - Download previous build or restore from backup
  - Deploy rollback
  - Run post-rollback health checks
  - Create rollback record
  - Create GitHub issue for incident tracking
  - Send notifications

**Requirements Validated:**
- ✅ Requirement 17.5: One-click rollback capability

**Features:**
- Supports rollback by backup ID or previous SHA
- Creates incident tracking issue
- Records rollback for audit trail
- Health checks after rollback

---

### 5. Lighthouse CI (`.github/workflows/lighthouse.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

**Jobs:**
- **Lighthouse Performance Audit**:
  - Build application
  - Run Lighthouse CI on all core pages
  - Parse and validate results
  - Upload Lighthouse reports
  - Generate performance summary
  - Comment PR with results

**Pages Audited:**
- Home (/)
- Dashboard
- Projects
- Pull Requests
- Architecture
- Analysis Queue
- Metrics

**Performance Thresholds:**
- Performance Score: ≥ 90% (required)
- Accessibility Score: ≥ 90% (warning)
- Best Practices Score: ≥ 90% (warning)
- SEO Score: ≥ 90% (warning)

**Core Web Vitals Thresholds:**
- First Contentful Paint (FCP): < 2000ms
- Largest Contentful Paint (LCP): < 2500ms
- Cumulative Layout Shift (CLS): < 0.1
- Total Blocking Time (TBT): < 300ms
- Speed Index (SI): < 3000ms

**Requirements Validated:**
- ✅ Requirement 14.1: Lighthouse score ≥ 90
- ✅ Requirement 14.5: Performance testing in CI/CD

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

The Lighthouse CI package (`@lhci/cli`) is included in devDependencies.

### 2. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

**Optional:**
- `LHCI_GITHUB_APP_TOKEN` - Lighthouse CI GitHub App token (for enhanced reporting)
- `PRODUCTION_API_URL` - Production API URL
- `CODECOV_TOKEN` - Codecov upload token (optional)

**For Deployment (customize based on your infrastructure):**
- SSH keys, cloud provider credentials, or deployment tokens

### 3. Customize Deployment Commands

The deployment workflows contain placeholder commands. Update them based on your infrastructure:

**Example deployment methods:**
- Docker: Build and push images
- SSH: rsync files to servers
- Cloud Providers: AWS, Azure, GCP CLI commands
- Platforms: Vercel, Netlify, etc.

Edit these files:
- `.github/workflows/deploy.yml` - Lines with deployment commands
- `.github/workflows/rollback.yml` - Lines with rollback commands

### 4. Configure Environments

Set up GitHub Environments for deployment protection:

1. Go to Settings → Environments
2. Create environments: `test`, `staging`, `production`
3. Configure protection rules:
   - **Production**: Require manual approval
   - **Test**: No restrictions
4. Add environment-specific secrets and variables

---

## Usage

### Running CI/CD Locally

**Run tests:**
```bash
npm run test:ci
```

**Run linting:**
```bash
npm run lint
```

**Run type checking:**
```bash
npm run type-check
```

**Build application:**
```bash
npm run build
```

**Run Lighthouse CI:**
```bash
npm run lighthouse:ci
```

### Manual Deployment

**Deploy to Test:**
1. Go to Actions → Deploy Pipeline
2. Click "Run workflow"
3. Select environment: `test`
4. Leave build_sha empty for latest
5. Click "Run workflow"

**Deploy to Production:**
1. Go to Actions → Deploy Pipeline
2. Click "Run workflow"
3. Select environment: `production`
4. Enter build_sha (optional, uses latest if empty)
5. Click "Run workflow"
6. Approve deployment (if protection rules enabled)

### Rollback

**Rollback by Backup ID:**
1. Go to Actions → Rollback Pipeline
2. Click "Run workflow"
3. Select environment
4. Enter backup_id (e.g., `backup-20240101-120000`)
5. Click "Run workflow"

**Rollback by Previous SHA:**
1. Find the previous successful deployment SHA
2. Go to Actions → Rollback Pipeline
3. Click "Run workflow"
4. Select environment
5. Enter previous_sha
6. Click "Run workflow"

---

## Monitoring and Notifications

### Build Status

Monitor build status in:
- GitHub Actions tab
- PR checks
- Commit status badges

### Coverage Reports

View coverage reports:
- In PR comments
- In GitHub Actions artifacts
- On Codecov (if configured)

### Lighthouse Reports

View Lighthouse reports:
- In PR comments
- In GitHub Actions step summary
- In uploaded artifacts

### Deployment Records

Deployment records are stored as artifacts:
- `deployment-{environment}-{sha}` - Deployment metadata
- `rollback-{environment}-{timestamp}` - Rollback metadata

---

## Troubleshooting

### CI Pipeline Fails

**Coverage below 80%:**
- Run `npm run test:coverage` locally
- Check which files need more tests
- Add tests to increase coverage

**Linting errors:**
- Run `npm run lint:fix` to auto-fix
- Manually fix remaining issues

**Type errors:**
- Run `npm run type-check` locally
- Fix TypeScript errors

### Build Pipeline Fails

**Build errors:**
- Check build logs in Actions
- Run `npm run build` locally
- Verify environment variables

**Artifact upload fails:**
- Check artifact size (max 10GB)
- Verify GitHub Actions permissions

### Deployment Fails

**Artifact not found:**
- Verify build SHA is correct
- Check artifact retention period (30 days)
- Re-run build if needed

**Health checks fail:**
- Check application logs
- Verify deployment completed
- Check server connectivity

### Lighthouse CI Fails

**Performance score below 90%:**
- Review Lighthouse report details
- Check Core Web Vitals metrics
- Optimize based on recommendations

**Server timeout:**
- Increase `startServerReadyTimeout` in `lighthouserc.json`
- Check if build is working locally

---

## Best Practices

### 1. Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature branches

### 2. Commit Messages

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance

### 3. Pull Requests

- Always create PR for changes
- Wait for CI checks to pass
- Review coverage and Lighthouse reports
- Get code review approval
- Squash and merge

### 4. Deployments

- Test in test environment first
- Monitor after deployment
- Keep deployment records
- Document any issues

### 5. Rollbacks

- Always create backup before production deploy
- Test rollback in test environment
- Document rollback reason
- Create incident issue

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review failed builds
- Check coverage trends
- Monitor Lighthouse scores

**Monthly:**
- Update dependencies
- Review and clean old artifacts
- Update deployment documentation

**Quarterly:**
- Review and optimize workflows
- Update Node.js versions
- Audit security practices

---

## Support

For issues or questions:
1. Check this documentation
2. Review workflow logs in GitHub Actions
3. Check deployment records
4. Create an issue in the repository

---

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ CI pipeline with lint, test, and coverage
- ✅ Build pipeline with artifact creation
- ✅ Deploy pipeline for test and production
- ✅ Rollback pipeline with backup support
- ✅ Lighthouse CI with performance thresholds
- ✅ PR comments for coverage and performance
- ✅ Deployment records and audit trail
