# System Architecture Improvements

Analysis and recommendations for architecture and configuration improvements.

## Current Architecture Summary

### Services
| Service | Port | Status | Dependencies |
|---------|------|--------|--------------|
| api-gateway | 3010→3000 | ✅ Comprehensive | redis |
| auth-service | 3001 | ✅ Full implementation | postgres, redis |
| code-review-engine | 3002 | ⚠️ Minimal | redis |
| architecture-analyzer | 3003 | ⚠️ Minimal | neo4j, redis |
| agentic-ai | 3004 | ⚠️ Minimal | neo4j, redis |
| project-manager | 3005 | ⚠️ Minimal | postgres, redis |
| llm-service | 8001→8000 | ✅ Full | GPU (optional) |
| backend (Python) | 8000 | ✅ Comprehensive | all |

### Infrastructure
- **PostgreSQL 16**: Primary database
- **Redis 7**: Caching, rate limiting, sessions
- **Neo4j 5.15**: Graph database for architecture data

---

## Identified Issues

### 1. Minimal Service Implementations
**Issue**: 4 TypeScript services have minimal stub implementations (~13-60 lines).

**Affected**:
- `services/agentic-ai/src/index.ts` - Only health endpoint
- `services/code-review-engine/src/index.ts` - Health + analyze endpoints only
- `services/architecture-analyzer` - Not found in src
- `services/project-manager` - Not found in src

**Recommendation**: Either consolidate into backend or expand implementations.

---

### 2. Duplicate LLM Client Code
**Issue**: `llm-client.ts` exists in 2 locations:
- `shared/llm-client.ts`
- `services/ai-service/src/code_review_engine/llm-client.ts`

**Recommendation**: Use shared version only via path aliases.

---

### 3. Memory Configuration
**Current**:
- LLM Service: 4GB limit
- Neo4j: 1GB limit
- Other services: 256MB limit

**Recommendation**: Consider increasing Neo4j limit for large codebases.

---

### 4. Service Consolidation Opportunity
**Observation**: `services/ai-service` contains subfolders for both `agentic_ai` and `code_review_engine`, duplicating the separate services.

**Recommendation**: Consolidate into single ai-service or remove duplicates.

---

## Configuration Improvements Made

### TypeScript Configuration
1. ✅ Excluded `shared/integration/**/*` from root tsconfig (frontend-only code)
2. ✅ Added DOM types to shared tsconfig for frontend integration
3. ✅ Fixed llm-client import path in code_review_engine

---

## Performance Recommendations

1. **Enable connection pooling** - Add PgBouncer for PostgreSQL
2. **Add Redis cluster** - For production scalability
3. **Implement service mesh** - Consider Istio/Linkerd for observability
4. **Add APM** - Integrate OpenTelemetry for distributed tracing

---

## Security Recommendations

1. **Secrets management** - Use Vault or cloud secrets manager
2. **mTLS** - Already have certs folder, enable service-to-service TLS
3. **Network policies** - Restrict inter-service communication in K8s
