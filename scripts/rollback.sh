#!/bin/bash
# ============================================================================
# Production Environment Rollback Script
# ============================================================================
# This script performs rollback operations to restore the system to a
# previous state using database backups.
#
# Usage: ./rollback.sh <backup_id>
# Example: ./rollback.sh 20240304_143022
# ============================================================================

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_DIR="$PROJECT_ROOT/logs"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/rollback_${TIMESTAMP}.log"

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
# Validation Functions
# ============================================================================

validate_backup_id() {
    local backup_id=$1
    
    if [ -z "$backup_id" ]; then
        log_error "Backup ID is required"
        echo ""
        echo "Usage: $0 <backup_id>"
        echo ""
        echo "Available backups:"
        list_available_backups
        exit 1
    fi
    
    local backup_file="$BACKUP_DIR/postgres_backup_${backup_id}.sql"
    local metadata_file="$BACKUP_DIR/postgres_backup_${backup_id}.json"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        echo ""
        echo "Available backups:"
        list_available_backups
        exit 1
    fi
    
    if [ ! -f "$metadata_file" ]; then
        log_warning "Backup metadata file not found: $metadata_file"
    fi
    
    log_success "Backup file found: $backup_file"
}

list_available_backups() {
    if [ ! -d "$BACKUP_DIR" ]; then
        echo "  No backups directory found"
        return
    fi
    
    local backups=$(ls -1 "$BACKUP_DIR"/postgres_backup_*.sql 2>/dev/null | sort -r)
    
    if [ -z "$backups" ]; then
        echo "  No backups available"
        return
    fi
    
    echo ""
    printf "  %-20s %-15s %-20s\n" "BACKUP ID" "SIZE" "DATE"
    printf "  %-20s %-15s %-20s\n" "--------------------" "---------------" "--------------------"
    
    for backup in $backups; do
        local backup_id=$(basename "$backup" .sql | sed 's/postgres_backup_//')
        local size=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup" 2>/dev/null || echo "0")
        local size_mb=$(echo "scale=2; $size / 1048576" | bc 2>/dev/null || echo "0")
        local date=$(echo "$backup_id" | sed 's/_/ /')
        
        printf "  %-20s %-15s %-20s\n" "$backup_id" "${size_mb}MB" "$date"
    done
    echo ""
}

# ============================================================================
# Rollback Functions
# ============================================================================

stop_services() {
    log_step "Step 1: Stopping Services"
    
    cd "$PROJECT_ROOT"
    
    log_info "Stopping Docker services..."
    
    if docker-compose -f docker-compose.production.yml down 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Services stopped successfully"
        return 0
    else
        log_warning "Failed to stop some services (may not be running)"
        return 0
    fi
}

restore_database() {
    log_step "Step 2: Restoring Database"
    
    local backup_id=$1
    local backup_file="$BACKUP_DIR/postgres_backup_${backup_id}.sql"
    local metadata_file="$BACKUP_DIR/postgres_backup_${backup_id}.json"
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env.production" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env.production" | grep -v '^$' | xargs)
    else
        log_error ".env.production file not found"
        return 1
    fi
    
    # Display backup metadata
    if [ -f "$metadata_file" ]; then
        log_info "Backup metadata:"
        cat "$metadata_file" | tee -a "$LOG_FILE"
        echo ""
    fi
    
    log_warning "This will DROP and RECREATE the database: $POSTGRES_DB"
    log_warning "All current data will be lost!"
    echo ""
    
    # Confirmation prompt
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled by user"
        exit 0
    fi
    
    log_info "Restoring database from backup: $backup_id"
    
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    # Drop existing database
    log_info "Dropping existing database..."
    if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $POSTGRES_DB;" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Database dropped"
    else
        log_error "Failed to drop database"
        return 1
    fi
    
    # Create new database
    log_info "Creating new database..."
    if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres \
        -c "CREATE DATABASE $POSTGRES_DB;" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Database created"
    else
        log_error "Failed to create database"
        return 1
    fi
    
    # Restore backup
    log_info "Restoring backup data..."
    if pg_restore -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" -F c "$backup_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Database restored successfully"
        return 0
    else
        # pg_restore may return non-zero even on success due to warnings
        if grep -qi "error" "$LOG_FILE"; then
            log_error "Database restore failed with errors"
            return 1
        else
            log_warning "Database restored with warnings (check log for details)"
            return 0
        fi
    fi
}

restart_services() {
    log_step "Step 3: Restarting Services"
    
    cd "$PROJECT_ROOT"
    
    log_info "Starting Docker services..."
    
    if docker-compose -f docker-compose.production.yml up -d 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Services started successfully"
        
        # Wait for services to be ready
        log_info "Waiting for services to be ready (30 seconds)..."
        sleep 30
        
        return 0
    else
        log_error "Failed to start services"
        return 1
    fi
}

verify_rollback() {
    log_step "Step 4: Verifying Rollback"
    
    local backend_url="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
    local max_retries=5
    local retry_delay=10
    
    log_info "Checking backend health at $backend_url/api/v1/health"
    
    for i in $(seq 1 $max_retries); do
        log_info "Health check attempt $i/$max_retries..."
        
        if curl -f -s "$backend_url/api/v1/health" > /dev/null 2>&1; then
            log_success "Backend health check passed"
            
            # Get detailed health status
            local health_response=$(curl -s "$backend_url/api/v1/health" 2>&1)
            log_info "Health status: $health_response"
            
            return 0
        else
            if [ $i -lt $max_retries ]; then
                log_warning "Health check failed, retrying in ${retry_delay}s..."
                sleep $retry_delay
            fi
        fi
    done
    
    log_error "Health checks failed after $max_retries attempts"
    log_warning "Services may need more time to start, or there may be configuration issues"
    return 1
}

# ============================================================================
# Main Rollback Function
# ============================================================================

main() {
    local backup_id=$1
    local start_time=$(date +%s)
    
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║           Production Environment Rollback Script              ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log_info "Rollback started at $(date)"
    log_info "Log file: $LOG_FILE"
    log_info "Backup ID: $backup_id"
    
    # Validate backup
    validate_backup_id "$backup_id"
    
    # Execute rollback steps
    local step_failed=false
    
    # Step 1: Stop services
    if ! stop_services; then
        step_failed=true
    fi
    
    # Step 2: Restore database
    if [ "$step_failed" = false ] && ! restore_database "$backup_id"; then
        step_failed=true
    fi
    
    # Step 3: Restart services
    if [ "$step_failed" = false ] && ! restart_services; then
        step_failed=true
    fi
    
    # Step 4: Verify rollback
    if [ "$step_failed" = false ]; then
        verify_rollback || log_warning "Verification incomplete, but rollback may have succeeded"
    fi
    
    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Report results
    if [ "$step_failed" = true ]; then
        log_error "Rollback failed!"
        echo ""
        log_error "Rollback failed! Check the log for details: $LOG_FILE"
        echo ""
        exit 1
    fi
    
    # Success!
    log_step "Rollback Completed Successfully!"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║              ✓ Rollback Completed Successfully!                ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log_success "Rollback completed in ${duration}s"
    log_info "System restored to backup: $backup_id"
    echo ""
    
    exit 0
}

# ============================================================================
# Error Handler
# ============================================================================

error_handler() {
    local line_no=$1
    log_error "Error occurred at line $line_no"
    log_error "Rollback failed - manual intervention may be required"
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

# Check for backup ID argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_id>"
    echo ""
    echo "Available backups:"
    list_available_backups
    exit 1
fi

# Run main function
main "$1"
