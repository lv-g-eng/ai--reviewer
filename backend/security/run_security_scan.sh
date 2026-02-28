#!/bin/bash
# OWASP ZAP Security Scan Runner Script
# This script simplifies running security scans against the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
SCAN_TYPE="${SCAN_TYPE:-baseline}"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/zap_reports}"

# Functions
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_info "Docker is available"
}

check_backend() {
    print_info "Checking if backend is accessible at $BACKEND_URL..."
    
    if curl -s -f "$BACKEND_URL/api/v1/health" > /dev/null 2>&1; then
        print_info "Backend is accessible"
        return 0
    elif curl -s -f "$BACKEND_URL" > /dev/null 2>&1; then
        print_warning "Backend is accessible but health endpoint not found"
        return 0
    else
        print_warning "Backend may not be accessible at $BACKEND_URL"
        print_warning "Make sure the backend is running before scanning"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

pull_zap_image() {
    print_info "Pulling latest OWASP ZAP Docker image..."
    docker pull owasp/zap2docker-stable
}

run_baseline_scan() {
    print_header "Running ZAP Baseline Scan"
    
    mkdir -p "$OUTPUT_DIR"
    
    docker run --rm \
        --network host \
        -v "$OUTPUT_DIR:/zap/wrk:rw" \
        owasp/zap2docker-stable \
        zap-baseline.py \
        -t "$BACKEND_URL" \
        -r baseline_report.html \
        -J baseline_report.json \
        -w baseline_report.md \
        -I
    
    print_info "Baseline scan complete"
    print_info "Reports saved to: $OUTPUT_DIR"
}

run_api_scan() {
    print_header "Running ZAP API Scan"
    
    mkdir -p "$OUTPUT_DIR"
    
    local api_spec="$BACKEND_URL/api/v1/openapi.json"
    print_info "Using API spec: $api_spec"
    
    docker run --rm \
        --network host \
        -v "$OUTPUT_DIR:/zap/wrk:rw" \
        owasp/zap2docker-stable \
        zap-api-scan.py \
        -t "$api_spec" \
        -f openapi \
        -r api_report.html \
        -J api_report.json \
        -w api_report.md \
        -I
    
    print_info "API scan complete"
    print_info "Reports saved to: $OUTPUT_DIR"
}

run_full_scan() {
    print_header "Running ZAP Full Scan"
    print_warning "Full scan may take significant time and generate load on the application"
    
    read -p "Continue with full scan? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Full scan cancelled"
        exit 0
    fi
    
    mkdir -p "$OUTPUT_DIR"
    
    docker run --rm \
        --network host \
        -v "$OUTPUT_DIR:/zap/wrk:rw" \
        owasp/zap2docker-stable \
        zap-full-scan.py \
        -t "$BACKEND_URL" \
        -r full_report.html \
        -J full_report.json \
        -w full_report.md \
        -I
    
    print_info "Full scan complete"
    print_info "Reports saved to: $OUTPUT_DIR"
}

parse_results() {
    print_header "Parsing Scan Results"
    
    local json_report=""
    
    case $SCAN_TYPE in
        baseline)
            json_report="$OUTPUT_DIR/baseline_report.json"
            ;;
        api)
            json_report="$OUTPUT_DIR/api_report.json"
            ;;
        full)
            json_report="$OUTPUT_DIR/full_report.json"
            ;;
    esac
    
    if [ ! -f "$json_report" ]; then
        print_warning "JSON report not found: $json_report"
        return
    fi
    
    # Count alerts by severity using jq if available
    if command -v jq &> /dev/null; then
        local high=$(jq '[.site[0].alerts[] | select(.riskdesc | startswith("High"))] | length' "$json_report")
        local medium=$(jq '[.site[0].alerts[] | select(.riskdesc | startswith("Medium"))] | length' "$json_report")
        local low=$(jq '[.site[0].alerts[] | select(.riskdesc | startswith("Low"))] | length' "$json_report")
        local info=$(jq '[.site[0].alerts[] | select(.riskdesc | startswith("Informational"))] | length' "$json_report")
        
        echo ""
        print_info "Scan Results Summary:"
        echo "  High Risk:          $high"
        echo "  Medium Risk:        $medium"
        echo "  Low Risk:           $low"
        echo "  Informational:      $info"
        echo ""
        
        # Check compliance (requirement: zero critical and high severity)
        if [ "$high" -eq 0 ]; then
            print_info "✅ PASS: Zero high severity vulnerabilities found"
        else
            print_error "❌ FAIL: $high high severity vulnerabilities found (requirement: 0)"
            return 1
        fi
    else
        print_warning "jq not installed, skipping result parsing"
        print_info "Install jq for detailed result analysis: apt-get install jq"
    fi
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run OWASP ZAP security scans against the application.

OPTIONS:
    -t, --type TYPE         Scan type: baseline, api, or full (default: baseline)
    -u, --url URL          Backend URL (default: http://localhost:8000)
    -o, --output DIR       Output directory for reports (default: ./zap_reports)
    -s, --skip-checks      Skip pre-flight checks
    -h, --help             Show this help message

EXAMPLES:
    # Run baseline scan
    $0 --type baseline

    # Run API scan against custom URL
    $0 --type api --url http://localhost:8000

    # Run full scan with custom output directory
    $0 --type full --output /tmp/zap_reports

ENVIRONMENT VARIABLES:
    BACKEND_URL            Backend URL to scan
    SCAN_TYPE              Type of scan to run
    OUTPUT_DIR             Output directory for reports

REQUIREMENTS:
    - Docker installed and running
    - Backend application running and accessible
    - Network connectivity to backend

COMPLIANCE:
    This scan verifies compliance with requirement 8.10:
    "THE System SHALL pass OWASP ZAP security scan with zero critical 
    and zero high severity vulnerabilities"

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            SCAN_TYPE="$2"
            shift 2
            ;;
        -u|--url)
            BACKEND_URL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -s|--skip-checks)
            SKIP_CHECKS=1
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header "OWASP ZAP Security Scanner"
    
    echo "Configuration:"
    echo "  Backend URL:    $BACKEND_URL"
    echo "  Scan Type:      $SCAN_TYPE"
    echo "  Output Dir:     $OUTPUT_DIR"
    echo ""
    
    # Pre-flight checks
    if [ -z "$SKIP_CHECKS" ]; then
        check_docker
        check_backend
        pull_zap_image
    fi
    
    # Run appropriate scan
    case $SCAN_TYPE in
        baseline)
            run_baseline_scan
            ;;
        api)
            run_api_scan
            ;;
        full)
            run_full_scan
            ;;
        *)
            print_error "Invalid scan type: $SCAN_TYPE"
            print_error "Valid types: baseline, api, full"
            exit 1
            ;;
    esac
    
    # Parse and display results
    parse_results
    local result=$?
    
    echo ""
    print_header "Scan Complete"
    print_info "View detailed reports in: $OUTPUT_DIR"
    
    if [ $result -eq 0 ]; then
        print_info "✅ Security scan PASSED"
        exit 0
    else
        print_error "❌ Security scan FAILED"
        print_error "Review the reports and fix identified vulnerabilities"
        exit 1
    fi
}

# Run main function
main
