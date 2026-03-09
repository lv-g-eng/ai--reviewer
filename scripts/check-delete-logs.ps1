# 检查删除操作的日志
Write-Host "=== Frontend Logs ===" -ForegroundColor Cyan
docker logs ai_review_frontend --tail 50 | Select-String -Pattern "DELETE|error|Error" -Context 1,1

Write-Host "`n=== Backend Logs ===" -ForegroundColor Cyan
docker logs ai_review_backend --tail 50 | Select-String -Pattern "DELETE|rbac/projects|error|Error|500" -Context 2,2

Write-Host "`n=== Recent Backend Activity ===" -ForegroundColor Cyan
docker logs ai_review_backend --tail 30
