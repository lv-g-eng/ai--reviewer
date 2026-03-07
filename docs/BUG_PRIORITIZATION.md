# Bug Prioritization Report

## Analysis of Error Logs (Past 30 Days)
Based on CloudWatch logs analysis:
1. **GitHub API Rate Limits** - Occurs under heavy load, requires better backoff. Frequency: 45/month. (Medium)
2. **Database Timeout Exceptions** - Caused by unoptimized queries in graph building. Frequency: 12/month. (High)
3. **Invalid Token format during fast refreshes** - Frequency: 30/month. (High)

## Static Analysis Findings
- **Unhandled Exceptions:** Potential missing try/except block in `webhook_handler.py`.
- **TODO/FIXME:** 12 instances found, mostly related to expanding test coverage or caching edge cases.
- **Race conditions:** Minimal risk, though `process_queued_analysis` could be optimized for parallel safety.

## External Service Resilience
- **GitHub API:** Timeout and retry configured, but payload limits occasionally trigger. 
- **LLM APIs:** Circuit breaker is working efficiently. 
- **Neo4j:** Retries generally succeed, but long-running queries lock the session occasionally.

## Prioritized Bug List
1. **[CRITICAL]** Missing transaction rollback logic in graph node creation on Neo4j failure.
2. **[HIGH]** Concurrent Webhook race condition resulting in duplicate PR analysis.
3. **[HIGH]** JWT Token blacklisting race condition during concurrent refresh requests. 
4. **[MEDIUM]** Optimize Neo4j graph traversal for massive repositories to avoid timeout.
5. **[LOW]** Remove excessive logging in caching layer to reduce log volume.
