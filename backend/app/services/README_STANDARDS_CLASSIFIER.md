# Standards Classifier Service

## Overview

The Standards Classifier Service integrates the `StandardsMapper` into the Code Review Service to automatically classify code review findings according to international standards:

- **ISO/IEC 25010**: Software quality characteristics and sub-characteristics
- **ISO/IEC 23396**: Software engineering practices
- **OWASP Top 10 2021**: Web application security vulnerabilities

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Code Review Service                       │
│                                                              │
│  ┌────────────────┐         ┌──────────────────────┐       │
│  │  CodeReviewer  │────────▶│ StandardsClassifier  │       │
│  └────────────────┘         └──────────────────────┘       │
│         │                              │                     │
│         │                              ▼                     │
│         │                    ┌──────────────────┐           │
│         │                    │ StandardsMapper  │           │
│         │                    │  (shared/        │           │
│         │                    │   standards.py)  │           │
│         │                    └──────────────────┘           │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────────────────────────────────┐            │
│  │         Database Models                     │            │
│  │  - ReviewComment (with standards fields)    │            │
│  │  - ArchitectureViolation (with standards)   │            │
│  └────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Automatic Classification

Every finding from code review is automatically classified with:
- ISO/IEC 25010 characteristic (e.g., "security", "maintainability")
- ISO/IEC 25010 sub-characteristic (e.g., "Confidentiality", "Analyzability")
- ISO/IEC 23396 practice ID (e.g., "SE-3", "SE-6")
- OWASP Top 10 reference (e.g., "A01:2021") for security findings

### 2. Enhanced Keyword Mapping

The classifier uses intelligent keyword matching to determine sub-characteristics:

**Security Sub-characteristics:**
- `authentication`, `password`, `mfa` → Authenticity
- `authorization`, `access_control` → Confidentiality
- `injection`, `xss`, `csrf` → Integrity
- `audit`, `logging` → Accountability

**Performance Sub-characteristics:**
- `slow`, `database`, `query` → Time Behaviour
- `memory`, `cpu`, `cache` → Resource Utilization
- `scalability` → Capacity

**Maintainability Sub-characteristics:**
- `complexity`, `readability`, `documentation` → Analyzability
- `duplication` → Reusability
- `coupling`, `cohesion` → Modularity
- `testability` → Testability

### 3. OWASP Mapping

Security findings are mapped to OWASP Top 10 2021 categories:

| OWASP ID | Category | Keywords |
|----------|----------|----------|
| A01:2021 | Broken Access Control | access control, authorization, privilege |
| A02:2021 | Cryptographic Failures | encryption, crypto, hardcoded secret |
| A03:2021 | Injection | sql injection, command injection |
| A04:2021 | Insecure Design | design flaw, security control |
| A05:2021 | Security Misconfiguration | configuration, default, misconfiguration |
| A06:2021 | Vulnerable Components | dependency, outdated, cve |
| A07:2021 | Authentication Failures | authentication, password policy, mfa |
| A08:2021 | Data Integrity Failures | deserialization, integrity |
| A09:2021 | Logging Failures | logging, monitoring, audit |
| A10:2021 | SSRF | ssrf, url, request forgery |

## Usage

### In Code Review Service

The `CodeReviewer` automatically applies standards classification:

```python
from app.services.code_reviewer import CodeReviewer

reviewer = CodeReviewer()
review_result = await reviewer.review_pull_request(pr_data, project_id, diff_content)

# All comments in review_result now have standards fields populated:
for comment in review_result.comments:
    print(f"ISO 25010: {comment.iso_25010_characteristic}")
    print(f"Sub-char: {comment.iso_25010_sub_characteristic}")
    print(f"ISO 23396: {comment.iso_23396_practice}")
    print(f"OWASP: {comment.owasp_reference}")
```

### Direct Classification

You can also use the classifier directly:

```python
from app.services.standards_classifier import get_standards_classifier

classifier = get_standards_classifier()

# Classify a single finding
finding = classifier.classify_finding(
    category="security",
    message="SQL injection vulnerability detected",
    severity="critical",
    file_path="app/api/users.py",
    line_number=42
)

print(f"ISO 25010: {finding.iso_25010_characteristic}")  # "security"
print(f"Sub-char: {finding.iso_25010_sub_characteristic}")  # "Integrity"
print(f"ISO 23396: {finding.iso_23396_practice}")  # "SE-6"
print(f"OWASP: {finding.owasp_reference}")  # "A03:2021"
```

### Batch Classification

```python
findings = [
    {"category": "security", "message": "SQL injection", "severity": "critical"},
    {"category": "performance", "message": "Slow query", "severity": "medium"},
]

classified = classifier.classify_findings_batch(findings)
```

### Standards Summary

```python
summary = classifier.get_standards_summary(classified_findings)

print(f"Total findings: {summary['total_findings']}")
print(f"ISO 25010 distribution: {summary['iso_25010_distribution']}")
print(f"ISO 23396 distribution: {summary['iso_23396_distribution']}")
print(f"OWASP distribution: {summary['owasp_distribution']}")
```

## Database Schema

### ReviewComment Model

```sql
CREATE TABLE review_comments (
    id UUID PRIMARY KEY,
    review_id UUID REFERENCES code_reviews(id),
    file_path VARCHAR(1024),
    line_number INTEGER,
    message TEXT,
    severity VARCHAR(32),
    category VARCHAR(64),
    
    -- Standards fields
    iso_25010_characteristic VARCHAR(128),
    iso_25010_sub_characteristic VARCHAR(128),
    iso_23396_practice VARCHAR(128),
    owasp_reference VARCHAR(128),
    
    created_at TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX idx_review_comments_iso25010 ON review_comments(iso_25010_characteristic);
CREATE INDEX idx_review_comments_iso23396 ON review_comments(iso_23396_practice);
CREATE INDEX idx_review_comments_owasp ON review_comments(owasp_reference);
```

### ArchitectureViolation Model

```sql
CREATE TABLE architecture_violations (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES architecture_analyses(id),
    type VARCHAR(64),
    component VARCHAR(256),
    message TEXT,
    severity VARCHAR(32),
    
    -- Standards fields
    iso_25010_characteristic VARCHAR(128),
    iso_25010_sub_characteristic VARCHAR(128),
    iso_23396_practice VARCHAR(128),
    owasp_reference VARCHAR(128)
);

-- Indexes
CREATE INDEX idx_arch_violations_iso25010 ON architecture_violations(iso_25010_characteristic);
CREATE INDEX idx_arch_violations_iso23396 ON architecture_violations(iso_23396_practice);
CREATE INDEX idx_arch_violations_owasp ON architecture_violations(owasp_reference);
```

## Migration

To add standards fields to existing database:

```bash
cd backend
alembic upgrade head
```

The migration file `add_standards_fields_to_findings.py` will:
1. Add standards columns to `review_comments` and `architecture_violations`
2. Create indexes for efficient querying
3. Support rollback if needed

## Testing

Run the test suite:

```bash
cd backend
python -m pytest tests/test_standards_classifier.py -v
```

Test coverage includes:
- ✅ Security findings with OWASP mapping
- ✅ Performance findings
- ✅ Maintainability findings
- ✅ Reliability findings
- ✅ Authentication/authorization findings
- ✅ Cryptographic findings
- ✅ Dependency findings
- ✅ Logging findings
- ✅ Batch classification
- ✅ Standards summary generation
- ✅ Unknown category handling
- ✅ Singleton pattern

## Requirements Validation

This implementation validates the following requirements:

- **Requirement 1.3**: Code violations are classified according to ISO/IEC 25010 quality characteristics ✅
- **Requirement 1.4**: Code violations are classified according to ISO/IEC 23396 engineering practices ✅
- **Requirement 8.2**: Findings are mapped to specific ISO/IEC 25010 sub-characteristics ✅
- **Requirement 8.3**: Engineering practices are evaluated using ISO/IEC 23396 guidelines ✅

## Design Properties

This implementation supports the following design properties:

- **Property 1: Standards Compliance Mapping**: Every finding is mapped to at least one valid ISO/IEC 25010 characteristic or ISO/IEC 23396 practice ✅
- **Property 3: Security Finding OWASP Reference**: Security findings include OWASP Top 10 references when applicable ✅

## Future Enhancements

1. **Machine Learning**: Train ML models to improve classification accuracy based on historical data
2. **Custom Mappings**: Allow organizations to define custom category-to-standard mappings
3. **Multi-language Support**: Extend keyword mappings for non-English codebases
4. **Confidence Scoring**: Implement confidence scores for classifications
5. **Standards Versioning**: Support multiple versions of standards (ISO 25010:2011 vs 2023)
6. **Compliance Reports**: Generate detailed compliance reports for audits

## References

- [ISO/IEC 25010:2011 - Systems and software Quality Requirements and Evaluation (SQuaRE)](https://www.iso.org/standard/35733.html)
- [ISO/IEC 23396:2020 - Software Engineering Practices](https://www.iso.org/standard/75404.html)
- [OWASP Top 10 2021](https://owasp.org/Top10/)
