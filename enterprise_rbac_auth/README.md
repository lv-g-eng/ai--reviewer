# Enterprise RBAC Authentication System

A secure, enterprise-level Role-Based Access Control (RBAC) authentication system built with FastAPI, featuring JWT-based authentication, fine-grained permissions, project isolation, and comprehensive audit logging.

## Features

- **JWT-based Authentication**: Secure token-based authentication with configurable expiration
- **Role-Based Access Control**: Three roles (Admin, Programmer, Visitor) with hierarchical permissions
- **Project Isolation**: Programmers can only access their own projects unless explicitly granted access
- **Authorization Middleware**: Reusable middleware for protecting API endpoints
- **Audit Logging**: Comprehensive logging of all sensitive operations for compliance
- **Session Management**: Support for concurrent sessions with automatic token refresh
- **Frontend Route Guards**: Protect routes and conditionally render UI based on permissions

## Project Structure

```
enterprise_rbac_auth/
├── models/          # Data models (User, Project, Session, AuditLog)
├── services/        # Business logic (Auth, RBAC, Audit services)
├── middleware/      # Authorization middleware
├── api/             # API endpoints
├── tests/           # Unit and property-based tests
├── config.py        # Configuration management
├── main.py          # Application entry point
└── requirements.txt # Python dependencies
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update the configuration:

```bash
cp .env.example .env
```

**Important**: Change the `JWT_SECRET_KEY` in production!

### 4. Initialize Database

```bash
python -m alembic upgrade head
```

### 5. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=enterprise_rbac_auth --cov-report=html
```

Run property-based tests only:

```bash
pytest -m property
```

## Roles and Permissions

### Admin
- Full system access
- User management (create, update, delete, view)
- Project management (all projects)
- Configuration management
- Audit log access

### Programmer
- Create and manage own projects
- View granted projects
- Export reports
- View configuration

### Visitor
- Read-only access to assigned projects

## Security Considerations

- All passwords are hashed using bcrypt (never stored in plaintext)
- JWT tokens have configurable expiration times
- Sessions can be invalidated on logout or password change
- Audit logs are immutable (write-only)
- The last Admin user cannot be deleted
- Generic error messages prevent username enumeration

## Development

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_auth_service.py

# With verbose output
pytest -v

# With coverage
pytest --cov
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## License

MIT License
