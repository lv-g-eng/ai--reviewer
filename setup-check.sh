#!/bin/bash

echo "=== AI Code Review Platform - Docker Stack Health Check ==="
echo

# Function to check if service is healthy
check_service() {
    local service_name=$1
    local container_name=$2
    local port=$3
    local url=$4
    
    echo "📊 Checking ${service_name}..."
    
    # Check container is running
    if docker ps | grep -q "${container_name}"; then
        echo "  ✅ Container ${container_name} is running"
        
        # Check health status
        local health_status=$(docker inspect --format='{{.State.Health.Status}}' ${container_name} 2>/dev/null || echo "unknown")
        echo "  📈 Health status: ${health_status}"
        
        # Check port connectivity
        if timeout 5 bash -c "echo > /dev/tcp/localhost/${port}" 2>/dev/null; then
            echo "  🔌 Port ${port} is accessible"
        else
            echo "  ❌ Port ${port} is not accessible"
        fi
        
        # Test service endpoint if URL provided
        if [ -n "$url" ]; then
            if curl -s -f "${url}" > /dev/null; then
                echo "  ✅ Service endpoint ${url} is responding"
            else
                echo "  ❌ Service endpoint ${url} is not responding"
            fi
        fi
        
    else
        echo "  ❌ Container ${container_name} is NOT running"
    fi
    echo
}

# Function to test database connections
test_database_connections() {
    echo "🧪 Testing Database Connections..."
    echo
    
    # Test PostgreSQL
    echo "🐘 Testing PostgreSQL connection..."
    if docker exec ai_review_postgres pg_isready -U postgres > /dev/null; then
        echo "  ✅ PostgreSQL connection successful"
        
        # Test basic query
        docker exec ai_review_postgres psql -U postgres -d ai_code_review -c "SELECT version();" 2>/dev/null | grep -q PostgreSQL
        if [ $? -eq 0 ]; then
            echo "  ✅ PostgreSQL database queries work"
        else
            echo "  ❌ PostgreSQL database queries failed"
        fi
    else
        echo "  ❌ PostgreSQL connection failed"
    fi
    echo
    
    # Test Redis
    echo "🔴 Testing Redis connection..."
    if docker exec ai_review_redis redis-cli -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q PONG; then
        echo "  ✅ Redis connection successful"
    else
        echo "  ❌ Redis connection failed"
    fi
    echo
    
    # Test Neo4j
    echo "🔗 Testing Neo4j connection..."
    if docker exec ai_review_neo4j cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1;" 2>/dev/null | grep -q "1"; then
        echo "  ✅ Neo4j connection successful"
    else
        echo "  ❌ Neo4j connection failed"
    fi
    echo
}

# Function to test application endpoints
test_endpoints() {
    echo "🌐 Testing Application Endpoints..."
    echo
    
    # Backend health check
    echo "🔧 Testing Backend API..."
    local backend_health_result=$(curl -s "http://localhost:8000/health")
    if [ $? -eq 0 ]; then
        echo "  ✅ Backend health check successful"
        echo "  📊 Response: $(echo ${backend_health_result} | jq -r '.status' 2>/dev/null || echo 'unknown')"
    else
        echo "  ❌ Backend health check failed"
    fi
    echo
    
    # Frontend health check (adjust if frontend has health endpoint)
    echo "💻 Testing Frontend..."
    local frontend_result=$(curl -s -I "http://localhost:3000")
    if echo "${frontend_result}" | grep -q "HTTP.*200"; then
        echo "  ✅ Frontend is responding"
    else
        echo "  ❌ Frontend is not responding"
    fi
    echo
    
    # pgAdmin check
    echo "📊 Testing pgAdmin..."
    local pgadmin_result=$(curl -s -I "http://localhost:5050")
    if echo "${pgadmin_result}" | grep -q "HTTP.*200"; then
        echo "  ✅ pgAdmin is accessible"
    else
        echo "  ❌ pgAdmin is not accessible"
    fi
    echo
}

# Main function
main() {
    # Source environment variables
    if [ -f .env ]; then
        source .env
        echo "✅ Environment variables loaded from .env"
    else
        echo "⚠️  No .env file found. Using default values."
        echo "   Please create .env file from .env.template"
    fi
    echo
    
    # Check Docker daemon
    echo "🐳 Checking Docker daemon..."
    if docker info > /dev/null 2>&1; then
        echo "  ✅ Docker daemon is running"
    else
        echo "  ❌ Docker daemon is not running"
        echo "  Please ensure Docker is installed and running"
        exit 1
    fi
    echo
    
    # Check each service
    check_service "PostgreSQL" "ai_review_postgres" "5432" ""
    check_service "pgAdmin" "ai_review_pgadmin" "5050" "http://localhost:5050"
    check_service "Neo4j" "ai_review_neo4j" "7474" "http://localhost:7474"
    check_service "Redis" "ai_review_redis" "6379" ""
    check_service "Backend API" "ai_review_backend" "8000" "http://localhost:8000/health"
    check_service "Frontend" "ai_review_frontend" "3000" "http://localhost:3000"
    check_service "Celery Worker" "ai_review_celery" "" ""
    check_service "Celery Beat" "ai_review_celery_beat" "" ""
    
    # Test database connections
    test_database_connections
    
    # Test application endpoints
    test_endpoints
    
    echo "=== Health Check Summary ==="
    echo "✅ Components passing: $(docker ps | grep ai_review | wc -l) containers running"
    echo "📊 Detailed status available above"
    echo
    echo "💡 Tips:"
    echo "   - Check logs: docker logs <container_name>"
    echo "   - View all containers: docker ps -a"
    echo "   - Restart stack: docker-compose restart"
    echo "   - View network: docker network inspect ai_review_network"
}

# Run main function
main