# API Gateway - Architecture Diagrams

> Visual representations of the API Gateway architecture, request flow, and component interactions

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Request Flow](#request-flow)
3. [Middleware Stack](#middleware-stack)
4. [Service Communication](#service-communication)
5. [Circuit Breaker States](#circuit-breaker-states)
6. [Rate Limiting Flow](#rate-limiting-flow)
7. [Error Handling Flow](#error-handling-flow)
8. [Production Deployment](#production-deployment)

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Web Application]
        MobileApp[Mobile App]
        CLI[CLI Tool]
        ThirdParty[Third-party Apps]
    end
    
    subgraph "Load Balancer"
        LB[Load Balancer<br/>Nginx/ALB]
    end
    
    subgraph "API Gateway Cluster :3000"
        GW1[Gateway Instance 1]
        GW2[Gateway Instance 2]
        GW3[Gateway Instance 3]
        
        subgraph "Middleware Stack"
            Security[Security Layer<br/>Helmet + CORS]
            CorrelationID[Correlation ID<br/>UUID Generation]
            RateLimit[Rate Limiter<br/>Redis-backed]
            Auth[Authentication<br/>JWT Validation]
            Validation[Request Validation<br/>Zod Schemas]
            CircuitBreaker[Circuit Breaker<br/>Opossum]
            Logging[Request/Response<br/>Logging]
        end
        
        subgraph "Core Services"
            Registry[Service Registry]
            Proxy[Service Proxy]
            HealthCheck[Health Monitor]
        end
    end
    
    subgraph "Infrastructure"
        Redis[(Redis Cluster<br/>Rate Limiting<br/>Session Storage)]
        Monitoring[Monitoring<br/>Logs & Metrics]
    end
    
    subgraph "Backend Microservices"
        AuthService[Auth Service<br/>:3001<br/>User Management]
        ReviewEngine[Code Review Engine<br/>:3002<br/>AI Analysis]
        ArchAnalyzer[Architecture Analyzer<br/>:3003<br/>Dependency Analysis]
        AgenticAI[Agentic AI<br/>:3004<br/>Task Queue]
        ProjectMgr[Project Manager<br/>:3005<br/>Project CRUD]
    end
    
    WebApp --> LB
    MobileApp --> LB
    CLI --> LB
    ThirdParty --> LB
    
    LB --> GW1
    LB --> GW2
    LB --> GW3
    
    GW1 --> Security
    GW2 --> Security
    GW3 --> Security
    
    Security --> CorrelationID
    CorrelationID --> RateLimit
    RateLimit --> Auth
    Auth --> Validation
    Validation --> CircuitBreaker
    CircuitBreaker --> Logging
    Logging --> Registry
    Registry --> Proxy
    
    GW1 -.->|Rate Limits| Redis
    GW2 -.->|Rate Limits| Redis
    GW3 -.->|Rate Limits| Redis
    
    Proxy -->|/api/v1/projects| ProjectMgr
    Proxy -->|/api/v1/reviews| ReviewEngine
    Proxy -->|/api/v1/architecture| ArchAnalyzer
    Proxy -->|/api/v1/queue| AgenticAI
    Proxy -->|/api/v1/admin| AuthService
    
    GW1 --> Monitoring
    GW2 --> Monitoring
    GW3 --> Monitoring
    
    style LB fill:#FF9800,stroke:#E65100,color:#fff
    style GW1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW2 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW3 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Redis fill:#DC382D,stroke:#A12622,color:#fff
    style AuthService fill:#2196F3,stroke:#1565C0,color:#fff
    style ReviewEngine fill:#2196F3,stroke:#1565C0,color:#fff
    style ArchAnalyzer fill:#2196F3,stroke:#1565C0,color:#fff
    style AgenticAI fill:#2196F3,stroke:#1565C0,color:#fff
    style ProjectMgr fill:#2196F3,stroke:#1565C0,color:#fff
```

---

## Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant LB as Load Balancer
    participant Gateway as API Gateway
    participant Redis
    participant Backend as Backend Service
    
    Client->>LB: HTTP Request
    LB->>Gateway: Route to Instance
    
    Note over Gateway: 1. Security Layer
    Gateway->>Gateway: Apply Helmet headers
    Gateway->>Gateway: Validate CORS
    
    Note over Gateway: 2. Generate Correlation ID
    Gateway->>Gateway: Create UUID
    
    Note over Gateway: 3. Rate Limiting
    Gateway->>Redis: Check rate limit
    Redis-->>Gateway: Limit status
    alt Rate limit exceeded
        Gateway-->>Client: 429 Too Many Requests
    end
    
    Note over Gateway: 4. Authentication
    Gateway->>Gateway: Extract JWT token
    Gateway->>Gateway: Verify token signature
    Gateway->>Gateway: Check expiration
    alt Invalid token
        Gateway-->>Client: 401 Unauthorized
    end
    
    Note over Gateway: 5. Request Validation
    Gateway->>Gateway: Validate with Zod schema
    alt Validation fails
        Gateway-->>Client: 400 Bad Request
    end
    
    Note over Gateway: 6. Circuit Breaker Check
    Gateway->>Gateway: Check circuit state
    alt Circuit open
        Gateway-->>Client: 503 Service Unavailable
    end
    
    Note over Gateway: 7. Log Request
    Gateway->>Gateway: Log request details
    
    Note over Gateway: 8. Proxy to Backend
    Gateway->>Backend: Forward request with headers
    Backend-->>Gateway: Response
    
    Note over Gateway: 9. Log Response
    Gateway->>Gateway: Log response + duration
    
    Gateway-->>LB: HTTP Response
    LB-->>Client: HTTP Response
```

---

## Middleware Stack

```mermaid
graph TD
    Start[Incoming Request] --> Security[Security Layer]
    
    Security --> |Helmet + CORS| CorrelationID[Correlation ID Middleware]
    
    CorrelationID --> |Generate UUID| ResponseTime[Response Time Tracker]
    
    ResponseTime --> ReqLogger[Request Logger]
    
    ReqLogger --> ReqMetadata[Request Metadata Logger]
    
    ReqMetadata --> ResLogger[Response Logger]
    
    ResLogger --> RateLimit[Rate Limiter]
    
    RateLimit --> |Check Redis| BodyParser[Body Parser]
    
    BodyParser --> |JSON/URL-encoded| HealthCheck{Health Check?}
    
    HealthCheck --> |Yes| HealthHandler[Health Handler]
    HealthCheck --> |No| Auth[Authentication]
    
    Auth --> |Verify JWT| Validation[Request Validation]
    
    Validation --> |Zod Schema| CircuitBreaker[Circuit Breaker]
    
    CircuitBreaker --> |Check State| Router[Route Handler]
    
    Router --> Proxy[Service Proxy]
    
    Proxy --> Backend[Backend Service]
    
    Backend --> CBError[Circuit Breaker Error Handler]
    
    CBError --> ErrorHandler[Global Error Handler]
    
    ErrorHandler --> Response[HTTP Response]
    
    HealthHandler --> Response
    
    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Response fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Security fill:#FF9800,stroke:#E65100,color:#fff
    style Auth fill:#FF9800,stroke:#E65100,color:#fff
    style RateLimit fill:#F44336,stroke:#C62828,color:#fff
    style CircuitBreaker fill:#F44336,stroke:#C62828,color:#fff
    style ErrorHandler fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

---

## Service Communication

```mermaid
graph LR
    Gateway[API Gateway<br/>:3000]
    
    subgraph "Backend Services"
        Auth[Auth Service<br/>:3001<br/>User Management]
        Review[Code Review Engine<br/>:3002<br/>AI Code Analysis]
        Arch[Architecture Analyzer<br/>:3003<br/>Dependency Analysis]
        AI[Agentic AI<br/>:3004<br/>Task Queue]
        Proj[Project Manager<br/>:3005<br/>Project CRUD]
    end
    
    Gateway -->|POST /api/auth/login| Auth
    Gateway -->|GET /api/v1/admin/*| Auth
    
    Gateway -->|POST /api/v1/reviews| Review
    Gateway -->|GET /api/v1/reviews/:id| Review
    
    Gateway -->|POST /api/v1/architecture/:id/scan| Arch
    Gateway -->|GET /api/v1/architecture/:id/graph| Arch
    
    Gateway -->|GET /api/v1/queue| AI
    Gateway -->|POST /api/v1/queue/:id/retry| AI
    
    Gateway -->|GET /api/v1/projects| Proj
    Gateway -->|POST /api/v1/projects| Proj
    
    style Gateway fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
    style Auth fill:#2196F3,stroke:#1565C0,color:#fff
    style Review fill:#2196F3,stroke:#1565C0,color:#fff
    style Arch fill:#2196F3,stroke:#1565C0,color:#fff
    style AI fill:#2196F3,stroke:#1565C0,color:#fff
    style Proj fill:#2196F3,stroke:#1565C0,color:#fff
```

---

## Circuit Breaker States

```mermaid
stateDiagram-v2
    [*] --> Closed: Initial State
    
    Closed --> Open: Error threshold exceeded<br/>(50% errors in 10 requests)
    
    Open --> HalfOpen: Reset timeout elapsed<br/>(60 seconds)
    
    HalfOpen --> Closed: Request succeeds
    HalfOpen --> Open: Request fails
    
    Closed --> Closed: Request succeeds
    
    note right of Closed
        Normal operation
        All requests pass through
        Tracking error rate
    end note
    
    note right of Open
        Failing fast
        Reject all requests
        Return 503 immediately
    end note
    
    note right of HalfOpen
        Testing recovery
        Allow one request
        Decide based on result
    end note
```

### Circuit Breaker Configuration

```typescript
{
  timeout: 10000,              // 10 seconds
  errorThresholdPercentage: 50, // 50% error rate
  resetTimeout: 60000,          // 60 seconds
  volumeThreshold: 10           // Minimum 10 requests
}
```

---

## Rate Limiting Flow

```mermaid
flowchart TD
    Start[Request Received] --> Extract[Extract Client IP]
    
    Extract --> Redis{Check Redis<br/>Rate Limit}
    
    Redis --> |Key exists| Count{Count < Max?}
    Redis --> |Key missing| Create[Create Key<br/>Count = 1<br/>TTL = Window]
    
    Count --> |Yes| Increment[Increment Count]
    Count --> |No| Reject[Return 429<br/>Too Many Requests]
    
    Increment --> Headers[Add Rate Limit Headers]
    Create --> Headers
    
    Headers --> Continue[Continue to<br/>Next Middleware]
    
    Reject --> End[End Request]
    Continue --> End
    
    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Reject fill:#F44336,stroke:#C62828,color:#fff
    style Continue fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Redis fill:#DC382D,stroke:#A12622,color:#fff
```

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1706097900
```

---

## Error Handling Flow

```mermaid
flowchart TD
    Error[Error Occurs] --> Type{Error Type?}
    
    Type --> |Validation Error| Validation[400 Bad Request]
    Type --> |Auth Error| Auth[401 Unauthorized]
    Type --> |Permission Error| Permission[403 Forbidden]
    Type --> |Not Found| NotFound[404 Not Found]
    Type --> |Rate Limit| RateLimit[429 Too Many Requests]
    Type --> |Circuit Breaker| CircuitBreaker[503 Service Unavailable]
    Type --> |Server Error| ServerError[500 Internal Server Error]
    
    Validation --> Format[Format Error Response]
    Auth --> Format
    Permission --> Format
    NotFound --> Format
    RateLimit --> Format
    CircuitBreaker --> Format
    ServerError --> Format
    
    Format --> AddCorrelation[Add Correlation ID]
    
    AddCorrelation --> Log{Production?}
    
    Log --> |Yes| HideStack[Hide Stack Trace]
    Log --> |No| ShowStack[Include Stack Trace]
    
    HideStack --> Response[Send JSON Response]
    ShowStack --> Response
    
    Response --> LogError[Log Error Details]
    
    LogError --> End[End Request]
    
    style Error fill:#F44336,stroke:#C62828,color:#fff
    style Response fill:#2196F3,stroke:#1565C0,color:#fff
    style End fill:#4CAF50,stroke:#2E7D32,color:#fff
```

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": ["Additional details"],
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-24T10:00:00.000Z"
  }
}
```

---

## Component Interaction

```mermaid
graph TB
    subgraph "API Gateway Components"
        Config[Configuration]
        Logger[Winston Logger]
        
        subgraph "Middleware"
            Security[Security]
            RateLimit[Rate Limiter]
            Auth[Authentication]
            Validation[Validation]
            CircuitBreaker[Circuit Breaker]
        end
        
        subgraph "Services"
            Registry[Service Registry]
            Proxy[Service Proxy]
        end
        
        subgraph "Routes"
            Projects[Projects Routes]
            Reviews[Reviews Routes]
            Architecture[Architecture Routes]
            Queue[Queue Routes]
            Admin[Admin Routes]
        end
        
        subgraph "Schemas"
            ProjectSchema[Project Schemas]
            ReviewSchema[Review Schemas]
            ArchSchema[Architecture Schemas]
        end
    end
    
    Config --> Logger
    Config --> Registry
    Config --> RateLimit
    Config --> Auth
    
    Logger --> Security
    Logger --> RateLimit
    Logger --> Auth
    Logger --> CircuitBreaker
    
    Registry --> Proxy
    
    Validation --> ProjectSchema
    Validation --> ReviewSchema
    Validation --> ArchSchema
    
    Projects --> Validation
    Reviews --> Validation
    Architecture --> Validation
    
    Projects --> Proxy
    Reviews --> Proxy
    Architecture --> Proxy
    Queue --> Proxy
    Admin --> Proxy
    
    style Config fill:#FF9800,stroke:#E65100,color:#fff
    style Logger fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style Registry fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Proxy fill:#4CAF50,stroke:#2E7D32,color:#fff
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx / ALB]
    end
    
    subgraph "API Gateway Cluster"
        GW1[Gateway Instance 1<br/>:3000]
        GW2[Gateway Instance 2<br/>:3000]
        GW3[Gateway Instance 3<br/>:3000]
    end
    
    subgraph "Shared Infrastructure"
        Redis[(Redis Cluster<br/>Rate Limiting)]
    end
    
    subgraph "Backend Services"
        Auth[Auth Service]
        Review[Code Review]
        Arch[Architecture]
        AI[Agentic AI]
        Proj[Project Manager]
    end
    
    Internet[Internet] --> LB
    
    LB --> GW1
    LB --> GW2
    LB --> GW3
    
    GW1 -.-> Redis
    GW2 -.-> Redis
    GW3 -.-> Redis
    
    GW1 --> Auth
    GW1 --> Review
    GW1 --> Arch
    GW1 --> AI
    GW1 --> Proj
    
    GW2 --> Auth
    GW2 --> Review
    GW2 --> Arch
    GW2 --> AI
    GW2 --> Proj
    
    GW3 --> Auth
    GW3 --> Review
    GW3 --> Arch
    GW3 --> AI
    GW3 --> Proj
    
    style LB fill:#FF9800,stroke:#E65100,color:#fff
    style GW1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW2 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW3 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Redis fill:#DC382D,stroke:#A12622,color:#fff
```

---

## Production Deployment

```mermaid
graph TB
    subgraph "Internet"
        Users[Users/Clients]
    end
    
    subgraph "CDN/Edge"
        CDN[CloudFlare CDN]
    end
    
    subgraph "Load Balancer Tier"
        ALB[Application Load Balancer<br/>AWS ALB / Nginx]
        SSL[SSL Termination<br/>TLS 1.3]
    end
    
    subgraph "API Gateway Cluster"
        subgraph "Availability Zone A"
            GW1[Gateway Instance 1<br/>Container/Pod]
            GW2[Gateway Instance 2<br/>Container/Pod]
        end
        
        subgraph "Availability Zone B"
            GW3[Gateway Instance 3<br/>Container/Pod]
            GW4[Gateway Instance 4<br/>Container/Pod]
        end
        
        subgraph "Auto Scaling"
            ASG[Auto Scaling Group<br/>Min: 2, Max: 10]
        end
    end
    
    subgraph "Shared Infrastructure"
        subgraph "Redis Cluster"
            Redis1[(Redis Primary)]
            Redis2[(Redis Replica 1)]
            Redis3[(Redis Replica 2)]
        end
        
        subgraph "Monitoring"
            Logs[Centralized Logging<br/>ELK/CloudWatch]
            Metrics[Metrics Collection<br/>Prometheus/CloudWatch]
            Alerts[Alerting<br/>PagerDuty/SNS]
        end
    end
    
    subgraph "Backend Services"
        subgraph "Service Mesh"
            AuthSvc[Auth Service<br/>Multiple Instances]
            ReviewSvc[Review Service<br/>Multiple Instances]
            ArchSvc[Architecture Service<br/>Multiple Instances]
            AISvc[AI Service<br/>Multiple Instances]
            ProjSvc[Project Service<br/>Multiple Instances]
        end
    end
    
    subgraph "Data Layer"
        DB[(Primary Database)]
        DBReplica[(Read Replicas)]
        Cache[(Application Cache)]
    end
    
    Users --> CDN
    CDN --> ALB
    ALB --> SSL
    SSL --> GW1
    SSL --> GW2
    SSL --> GW3
    SSL --> GW4
    
    ASG -.-> GW1
    ASG -.-> GW2
    ASG -.-> GW3
    ASG -.-> GW4
    
    GW1 -.-> Redis1
    GW2 -.-> Redis1
    GW3 -.-> Redis1
    GW4 -.-> Redis1
    
    Redis1 --> Redis2
    Redis1 --> Redis3
    
    GW1 --> AuthSvc
    GW1 --> ReviewSvc
    GW1 --> ArchSvc
    GW1 --> AISvc
    GW1 --> ProjSvc
    
    GW2 --> AuthSvc
    GW2 --> ReviewSvc
    GW2 --> ArchSvc
    GW2 --> AISvc
    GW2 --> ProjSvc
    
    GW3 --> AuthSvc
    GW3 --> ReviewSvc
    GW3 --> ArchSvc
    GW3 --> AISvc
    GW3 --> ProjSvc
    
    GW4 --> AuthSvc
    GW4 --> ReviewSvc
    GW4 --> ArchSvc
    GW4 --> AISvc
    GW4 --> ProjSvc
    
    AuthSvc --> DB
    ReviewSvc --> DB
    ArchSvc --> DB
    AISvc --> DB
    ProjSvc --> DB
    
    AuthSvc --> DBReplica
    ReviewSvc --> DBReplica
    ArchSvc --> DBReplica
    AISvc --> DBReplica
    ProjSvc --> DBReplica
    
    AuthSvc --> Cache
    ReviewSvc --> Cache
    ArchSvc --> Cache
    AISvc --> Cache
    ProjSvc --> Cache
    
    GW1 --> Logs
    GW2 --> Logs
    GW3 --> Logs
    GW4 --> Logs
    
    GW1 --> Metrics
    GW2 --> Metrics
    GW3 --> Metrics
    GW4 --> Metrics
    
    Metrics --> Alerts
    
    style CDN fill:#FF9800,stroke:#E65100,color:#fff
    style ALB fill:#FF9800,stroke:#E65100,color:#fff
    style GW1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW2 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW3 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GW4 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Redis1 fill:#DC382D,stroke:#A12622,color:#fff
    style Redis2 fill:#DC382D,stroke:#A12622,color:#fff
    style Redis3 fill:#DC382D,stroke:#A12622,color:#fff
    style AuthSvc fill:#2196F3,stroke:#1565C0,color:#fff
    style ReviewSvc fill:#2196F3,stroke:#1565C0,color:#fff
    style ArchSvc fill:#2196F3,stroke:#1565C0,color:#fff
    style AISvc fill:#2196F3,stroke:#1565C0,color:#fff
    style ProjSvc fill:#2196F3,stroke:#1565C0,color:#fff
```

### Production Deployment Features

**High Availability**
- Multi-AZ deployment across availability zones
- Auto-scaling based on CPU/memory/request metrics
- Load balancer health checks
- Circuit breaker protection

**Security**
- SSL/TLS termination at load balancer
- WAF (Web Application Firewall) protection
- VPC network isolation
- Security groups and NACLs

**Performance**
- CDN for static content and edge caching
- Redis cluster for distributed rate limiting
- Connection pooling and keep-alive
- Response compression

**Monitoring & Observability**
- Centralized logging with correlation IDs
- Real-time metrics collection
- Automated alerting
- Distributed tracing

**Scalability**
- Horizontal auto-scaling (2-10 instances)
- Database read replicas
- Application-level caching
- Service mesh for inter-service communication

---

**Last Updated**: January 24, 2026  
**Version**: 1.0.0
