#!/bin/bash
# ============================================================================
# Production Environment Migration Script
# ============================================================================
# This script automates the complete migration to production environment:
# 1. Prerequisite checks (environment variables, database connections)
# 2. Automatic backup creation
# 3. Database migration application
# 4. Frontend and backend deployment
# 5. Deployment validation (health checks, smoke tests)
# 6. Automatic rollback on failure
# 7. Migration report generation
# ============================================================================

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
REPORT_DIR="$PROJECT_ROOT/migration-reports"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Create directories if they don't exist
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"
mkdir -p "$BACKUP_DIR"

# Log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/migration_${TIMESTAMP}.log"
REPORT_FILE="$REPORT_DIR/migration_report_${TIMESTAMP}.md"

# Migration state tracking
MIGRATION_STATE_FILE="$PROJECT_ROOT/.migration_state"
BACKUP_ID=""
MIGRATION_STARTED=false
ROLLBACK_REQUIRED=false

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================================
# Logging Functions
# ============================================================================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $@" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $@" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "\n${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}$@${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}========================================${NC}\n" | tee -a "$LOG_FILE"
}

# ============================================================================
# State Management Functions
# ============================================================================

save_migration_state() {
    cat > "$MIGRATION_STATE_FILE" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "backup_id": "$BACKUP_ID",
  "migration_started": $MIGRATION_STARTED,
  "rollback_required": $ROLLBACK_REQUIRED,
  "log_file": "$LOG_FILE",
  "report_file": "$REPORT_FILE"
}
EOF
}

load_migration_state() {
    if [ -f "$MIGRATION_STATE_FILE" ]; then
        log_info "Loading previous migration state..."
        cat "$MIGRATION_STATE_FILE"
    fi
}

clear_migration_state() {
    if [ -f "$MIGRATION_STATE_FILE" ]; then
        rm "$MIGRATION_STATE_FILE"
        log_info "Migration state cleared"
    fi
}

# ============================================================================
# Report Generation Functions
# ============================================================================

init_report() {
    cat > "$REPORT_FILE" <<EOF
# Production Environment Migration Report

**Migration Date:** $(date +"%Y-%m-%d %H:%M:%S")  
**Migration ID:** ${TIMESTAMP}  
**Log File:** ${LOG_FILE}

---

## Migration Summary

EOF
}

add_report_section() {
    local title=$1
    local content=$2
    cat >> "$REPORT_FILE" <<EOF

### $title

$content

EOF
}

finalize_report() {
    local status=$1
    local duration=$2
    
    cat >> "$REPORT_FILE" <<EOF

---

## Final Status

**Status:** $status  
**Duration:** ${duration}s  
**Completed At:** $(date +"%Y-%m-%d %H:%M:%S")

EOF

    if [ "$status" = "SUCCESS" ]; then
        cat >> "$REPORT_FILE" <<EOF
✅ Migration completed successfully!

All systems are operational and validated.
EOF
    else
        cat >> "$REPORT_FILE" <<EOF
❌ Migration failed!

Please review the log file for detailed error information: \`${LOG_FILE}\`

EOF
        if [ -n "$BACKUP_ID" ]; then
            cat >> "$REPORT_FILE" <<EOF
A backup was created before migration: \`${BACKUP_ID}\`

To rollback, run:
\`\`\`bash
./scripts/rollback.sh $BACKUP_ID
\`\`\`
EOF
        fi
    fi
    
    log_info "Migration report generated: $REPORT_FILE"
}

# ============================================================================
# Prerequisite Check Functions
# ============================================================================

check_prerequisites() {
    log_step "Step 1: Checking Prerequisites"
    
    local errors=0
    
    # Check if .env.production exists
    if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
        log_error ".env.production file not found"
        ((errors++))
    else
        log_success ".env.production file found"
    fi
    
    # Check if validation script exists
    if [ ! -f "$SCRIPT_DIR/validate-production-env.sh" ]; then
        log_error "validate-production-env.sh script not found"
        ((errors++))
    else
        log_success "Validation script found"
    fi
    
    # Check if database connection test script exists
    if [ ! -f "$SCRIPT_DIR/test_db_connections.py" ]; then
        log_error "test_db_connections.py script not found"
        ((errors++))
    else
        log_success "Database connection test script found"
    fi
    
    # Check for required commands
    local required_commands=("docker" "docker-compose" "python3" "pg_dump" "psql")
    for cmd in "${required_commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            log_success "Command available: $cmd"
        else
            log_error "Required command not found: $cmd"
            ((errors++))
        fi
    done
    
    if [ $errors -gt 0 ]; then
        log_error "Prerequisite checks failed with $errors error(s)"
        add_report_section "Prerequisite Checks" "❌ Failed with $errors error(s)"
        return 1
    fi
    
    log_success "All prerequisite checks passed"
    add_report_section "Prerequisite Checks" "✅ All checks passed"
    return 0
}

validate_environment() {
    log_step "Step 2: Validating Environment Configuration"
    
    # Run environment validation script
    if bash "$SCRIPT_DIR/validate-production-env.sh"; then
        log_success "Environment validation passed"
        add_report_section "Environment Validation" "✅ All environment variables validated"
        return 0
    else
        log_error "Environment validation failed"
        add_report_section "Environment Validation" "❌ Validation failed - check log for details"
        return 1
    fi
}

test_database_connections() {
    log_step "Step 3: Testing Database Connections"
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env.production" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env.production" | grep -v '^$' | xargs)
    fi
    
    # Run database connection tests
    if python3 "$SCRIPT_DIR/test_db_connections.py"; then
        log_success "Database connection tests passed"
        add_report_section "Database Connections" "✅ All database connections successful"
        return 0
    else
        log_error "Database connection tests failed"
        add_report_section "Database Connections" "❌ Connection tests failed"
        return 1
    fi
}

# ============================================================================
# Backup Functions
# ============================================================================

create_backup() {
    log_step "Step 4: Creating Database Backup"
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env.production" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env.production" | grep -v '^$' | xargs)
    fi
    
    BACKUP_ID=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/postgres_backup_${BACKUP_ID}.sql"
    local metadata_file="$BACKUP_DIR/postgres_backup_${BACKUP_ID}.json"
    
    log_info "Creating PostgreSQL backup: $BACKUP_ID"
    
    # Create PostgreSQL backup
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    if pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -F c -f "$backup_file" 2>&1 | tee -a "$LOG_FILE"; then
        local backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
        log_success "PostgreSQL backup created: $backup_file (${backup_size} bytes)"
        
        # Create metadata file
        cat > "$metadata_file" <<EOF
{
  "backup_id": "$BACKUP_ID",
  "timestamp": "$(date -Iseconds)",
  "database": "$POSTGRES_DB",
  "host": "$POSTGRES_HOST",
  "backup_file": "$backup_file",
  "size_bytes": $backup_size
}
EOF
        
        log_success "Backup metadata saved: $metadata_file"
        add_report_section "Database Backup" "✅ Backup created successfully\n\n- **Backup ID:** $BACKUP_ID\n- **Size:** ${backup_size} bytes\n- **Location:** $backup_file"
        
        # Save state
        save_migration_state
        
        return 0
    else
        log_error "Failed to create PostgreSQL backup"
        add_report_section "Database Backup" "❌ Backup creation failed"
        return 1
    fi
}

# ============================================================================
# Database Migration Functions
# ============================================================================

apply_database_migrations() {
    log_step "Step 5: Applying Database Migrations"
    
    MIGRATION_STARTED=true
    save_migration_state
    
    cd "$PROJECT_ROOT/backend"
    
    log_info "Checking migration status..."
    
    # Check for pending migrations using Python
    local migration_check=$(python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from app.database.migration_manager import get_migration_manager

async def check():
    manager = get_migration_manager()
    status = await manager.get_migration_status()
    print(f'Pending: {status.pending_count}, Applied: {status.applied_count}')
    return status.pending_count

try:
    pending = asyncio.run(check())
    sys.exit(0 if pending >= 0 else 1)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)
    
    if [ $? -eq 0 ]; then
        log_info "Migration status: $migration_check"
        
        # Apply migrations using Python
        log_info "Applying pending migrations..."
        
        if python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from app.database.migration_manager import get_migration_manager

async def apply():
    manager = get_migration_manager()
    status = await manager.apply_pending_migrations()
    
    if status.errors:
        print('Migration errors:', file=sys.stderr)
        for error in status.errors:
            print(f'  - {error}', file=sys.stderr)
        return False
    
    print(f'Migrations applied: {status}')
    return True

try:
    success = asyncio.run(apply())
    sys.exit(0 if success else 1)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Database migrations applied successfully"
            add_report_section "Database Migrations" "✅ Migrations applied successfully"
            cd "$PROJECT_ROOT"
            return 0
        else
            log_error "Database migration failed"
            add_report_section "Database Migrations" "❌ Migration failed - check log for details"
            ROLLBACK_REQUIRED=true
            save_migration_state
            cd "$PROJECT_ROOT"
            return 1
        fi
    else
        log_error "Failed to check migration status"
        add_report_section "Database Migrations" "❌ Failed to check migration status"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

# ============================================================================
# Deployment Functions
# ============================================================================

deploy_services() {
    log_step "Step 6: Deploying Services"
    
    cd "$PROJECT_ROOT"
    
    log_info "Building and deploying services with docker-compose..."
    
    # Build images
    log_info "Building Docker images..."
    if docker-compose -f docker-compose.production.yml build 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Docker images built successfully"
    else
        log_error "Failed to build Docker images"
        add_report_section "Service Deployment" "❌ Failed to build Docker images"
        ROLLBACK_REQUIRED=true
        save_migration_state
        return 1
    fi
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f docker-compose.production.yml down 2>&1 | tee -a "$LOG_FILE" || true
    
    # Start services
    log_info "Starting services..."
    if docker-compose -f docker-compose.production.yml up -d 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Services started successfully"
        
        # Wait for services to be ready
        log_info "Waiting for services to be ready (60 seconds)..."
        sleep 60
        
        add_report_section "Service Deployment" "✅ Services deployed successfully"
        return 0
    else
        log_error "Failed to start services"
        add_report_section "Service Deployment" "❌ Failed to start services"
        ROLLBACK_REQUIRED=true
        save_migration_state
        return 1
    fi
}

# ============================================================================
# Validation Functions
# ============================================================================

run_health_checks() {
    log_step "Step 7: Running Health Checks"
    
    local max_retries=10
    local retry_delay=10
    local backend_url="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
    
    log_info "Checking backend health at $backend_url/api/v1/health"
    
    for i in $(seq 1 $max_retries); do
        log_info "Health check attempt $i/$max_retries..."
        
        if curl -f -s "$backend_url/api/v1/health" > /dev/null 2>&1; then
            log_success "Backend health check passed"
            
            # Get detailed health status
            local health_response=$(curl -s "$backend_url/api/v1/health" 2>&1)
            log_info "Health status: $health_response"
            
            add_report_section "Health Checks" "✅ All health checks passed\n\n\`\`\`json\n$health_response\n\`\`\`"
            return 0
        else
            log_warning "Health check failed, retrying in ${retry_delay}s..."
            sleep $retry_delay
        fi
    done
    
    log_error "Health checks failed after $max_retries attempts"
    add_report_section "Health Checks" "❌ Health checks failed after $max_retries attempts"
    ROLLBACK_REQUIRED=true
    save_migration_state
    return 1
}

run_smoke_tests() {
    log_step "Step 8: Running Smoke Tests"
    
    local backend_url="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
    local errors=0
    
    log_info "Running smoke tests against $backend_url"
    
    # Test 1: Health endpoint
    log_info "Test 1: Health endpoint"
    if curl -f -s "$backend_url/api/v1/health" > /dev/null; then
        log_success "✓ Health endpoint responding"
    else
        log_error "✗ Health endpoint failed"
        ((errors++))
    fi
    
    # Test 2: Readiness endpoint
    log_info "Test 2: Readiness endpoint"
    if curl -f -s "$backend_url/api/v1/health/ready" > /dev/null; then
        log_success "✓ Readiness endpoint responding"
    else
        log_error "✗ Readiness endpoint failed"
        ((errors++))
    fi
    
    # Test 3: Liveness endpoint
    log_info "Test 3: Liveness endpoint"
    if curl -f -s "$backend_url/api/v1/health/live" > /dev/null; then
        log_success "✓ Liveness endpoint responding"
    else
        log_error "✗ Liveness endpoint failed"
        ((errors++))
    fi
    
    # Test 4: Metrics endpoint
    log_info "Test 4: Metrics endpoint"
    if curl -f -s "$backend_url/metrics" > /dev/null; then
        log_success "✓ Metrics endpoint responding"
    else
        log_warning "⚠ Metrics endpoint not responding (non-critical)"
    fi
    
    # Test 5: Frontend health
    log_info "Test 5: Frontend health"
    if curl -f -s "http://localhost:3000/api/health" > /dev/null 2>&1; then
        log_success "✓ Frontend responding"
    else
        log_warning "⚠ Frontend not responding (may need more time)"
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "All critical smoke tests passed"
        add_report_section "Smoke Tests" "✅ All critical smoke tests passed (5/5)"
        return 0
    else
        log_error "Smoke tests failed: $errors critical test(s) failed"
        add_report_section "Smoke Tests" "❌ $errors critical test(s) failed"
        ROLLBACK_REQUIRED=true
        save_migration_state
        return 1
    fi
}

# ============================================================================
# Rollback Functions
# ============================================================================

perform_rollback() {
    log_step "ROLLBACK: Reverting Changes"
    
    if [ -z "$BACKUP_ID" ]; then
        log_error "No backup ID available for rollback"
        return 1
    fi
    
    log_warning "Initiating automatic rollback..."
    
    # Stop services
    log_info "Stopping services..."
    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.production.yml down 2>&1 | tee -a "$LOG_FILE" || true
    
    # Restore database backup
    log_info "Restoring database from backup: $BACKUP_ID"
    
    if [ -f "$SCRIPT_DIR/rollback.sh" ]; then
        if bash "$SCRIPT_DIR/rollback.sh" "$BACKUP_ID" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Database restored from backup"
            add_report_section "Rollback" "✅ Database restored from backup $BACKUP_ID"
        else
            log_error "Failed to restore database from backup"
            add_report_section "Rollback" "❌ Failed to restore database - manual intervention required"
            return 1
        fi
    else
        log_error "Rollback script not found"
        add_report_section "Rollback" "❌ Rollback script not found - manual intervention required"
        return 1
    fi
    
    # Restart services with previous configuration
    log_info "Restarting services..."
    docker-compose -f docker-compose.production.yml up -d 2>&1 | tee -a "$LOG_FILE" || true
    
    log_warning "Rollback completed - system restored to previous state"
    return 0
}

# ============================================================================
# Cleanup Functions
# ============================================================================

cleanup() {
    log_info "Performing cleanup..."
    
    # Remove old backups (keep last 10)
    if [ -d "$BACKUP_DIR" ]; then
        local backup_count=$(ls -1 "$BACKUP_DIR"/postgres_backup_*.sql 2>/dev/null | wc -l)
        if [ $backup_count -gt 10 ]; then
            log_info "Removing old backups (keeping last 10)..."
            ls -1t "$BACKUP_DIR"/postgres_backup_*.sql | tail -n +11 | xargs rm -f
            ls -1t "$BACKUP_DIR"/postgres_backup_*.json | tail -n +11 | xargs rm -f
        fi
    fi
    
    # Remove old logs (keep last 30 days)
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "migration_*.log" -mtime +30 -delete 2>/dev/null || true
    fi
    
    log_info "Cleanup completed"
}

# ============================================================================
# Main Migration Function
# ============================================================================

main() {
    local start_time=$(date +%s)
    
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║        Production Environment Migration Script                ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log_info "Migration started at $(date)"
    log_info "Log file: $LOG_FILE"
    log_info "Report file: $REPORT_FILE"
    
    # Initialize report
    init_report
    
    # Check for existing migration state
    load_migration_state
    
    # Execute migration steps
    local step_failed=false
    
    # Step 1: Prerequisites
    if ! check_prerequisites; then
        step_failed=true
    fi
    
    # Step 2: Environment validation
    if [ "$step_failed" = false ] && ! validate_environment; then
        step_failed=true
    fi
    
    # Step 3: Database connections
    if [ "$step_failed" = false ] && ! test_database_connections; then
        step_failed=true
    fi
    
    # Step 4: Create backup
    if [ "$step_failed" = false ] && ! create_backup; then
        step_failed=true
    fi
    
    # Step 5: Apply migrations
    if [ "$step_failed" = false ] && ! apply_database_migrations; then
        step_failed=true
    fi
    
    # Step 6: Deploy services
    if [ "$step_failed" = false ] && ! deploy_services; then
        step_failed=true
    fi
    
    # Step 7: Health checks
    if [ "$step_failed" = false ] && ! run_health_checks; then
        step_failed=true
    fi
    
    # Step 8: Smoke tests
    if [ "$step_failed" = false ] && ! run_smoke_tests; then
        step_failed=true
    fi
    
    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Handle failure and rollback
    if [ "$step_failed" = true ] || [ "$ROLLBACK_REQUIRED" = true ]; then
        log_error "Migration failed!"
        
        # Perform automatic rollback
        perform_rollback
        
        # Finalize report
        finalize_report "FAILED" "$duration"
        
        # Cleanup
        cleanup
        
        echo ""
        log_error "Migration failed! Check the report for details: $REPORT_FILE"
        echo ""
        
        exit 1
    fi
    
    # Success!
    log_step "Migration Completed Successfully!"
    
    # Cleanup
    cleanup
    
    # Clear migration state
    clear_migration_state
    
    # Finalize report
    finalize_report "SUCCESS" "$duration"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║              ✓ Migration Completed Successfully!               ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log_success "Migration completed in ${duration}s"
    log_info "Report: $REPORT_FILE"
    echo ""
    
    exit 0
}

# ============================================================================
# Error Handler
# ============================================================================

error_handler() {
    local line_no=$1
    log_error "Error occurred at line $line_no"
    
    if [ "$ROLLBACK_REQUIRED" = true ] || [ "$MIGRATION_STARTED" = true ]; then
        log_warning "Attempting automatic rollback..."
        perform_rollback
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    finalize_report "FAILED" "$duration"
    
    exit 1
}

trap 'error_handler $LINENO' ERR

# ============================================================================
# Script Entry Point
# ============================================================================

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    log_warning "Running as root is not recommended"
fi

# Run main function
main "$@"
