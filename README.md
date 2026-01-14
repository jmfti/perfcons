# Perfcons - Facts and Budgets Management API

A REST API built with FastAPI and MariaDB for managing facts and budgets associated with conversation IDs.

## Features

- **FastAPI** REST API with automatic Swagger documentation
- **MariaDB** database with named volume for data persistence
- **Bearer Token Authentication** for secure API access
- **CRUD Operations** for facts and budgets associated with conversation IDs
- **Integration Tests** with unittest
- **Docker Compose** stack for easy deployment
- **Large Text Support** - Facts can store >8KB of text, budgets can store >100KB of text

## Project Structure

```
perfcons/
├── app/
│   ├── src/
│   │   └── main.py          # FastAPI application
│   ├── Dockerfile           # Docker image for API
│   └── requirements.txt     # Python dependencies
├── tests/
│   └── test_integration.py  # Integration tests
├── docker-compose.yml       # Docker Compose configuration
├── Makefile                 # Deployment commands
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for running tests locally)

### 1. Build and Start Services

```bash
make build
make up
```

The API will be available at `http://localhost:8000`  
Swagger documentation at `http://localhost:8000/docs`

### 2. Set API Token (Optional)

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` to set your custom configuration:

```
API_TOKEN=your-secret-token-here
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_DATABASE=perfcons
MYSQL_USER=your-db-user
MYSQL_PASSWORD=your-db-password
```

**Important**: For production deployments, always change the default passwords and API token!

Then restart services:

```bash
make restart
```

### 3. Run Integration Tests

Install test dependencies:

```bash
pip install requests
```

Run tests:

```bash
make test
```

## API Endpoints

All endpoints require Bearer token authentication via the `Authorization` header and conversation ID via the `X-Conversation-ID` header (except `/facts/all`, `/budgets/all` and `/health`).

### Authentication

```
Authorization: Bearer <your-api-token>
```

### Create Fact

```bash
POST /facts
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
Body:
  {
    "fact": "Your fact text here"
  }
```

### Read Fact

```bash
GET /facts
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
```

### Update Fact

```bash
PUT /facts
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
Body:
  {
    "fact": "Updated fact text"
  }
```

### Delete Fact

```bash
DELETE /facts
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
```

### List All Facts

```bash
GET /facts/all
Headers:
  Authorization: Bearer my-secret-token
```

### Health Check

```bash
GET /health
```

## Budget Endpoints

### Create Budget

```bash
POST /budgets
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
Body:
  {
    "budget": "Your budget text here"
  }
```

### Read Budget

```bash
GET /budgets
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
```

### Update Budget

```bash
PUT /budgets
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
Body:
  {
    "budget": "Updated budget text"
  }
```

### Delete Budget

```bash
DELETE /budgets
Headers:
  Authorization: Bearer my-secret-token
  X-Conversation-ID: conversation-123
```

### List All Budgets

```bash
GET /budgets/all
Headers:
  Authorization: Bearer my-secret-token
```

## Example Usage with curl

```bash
# Create a fact
curl -X POST http://localhost:8000/facts \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001" \
  -H "Content-Type: application/json" \
  -d '{"fact": "This is a sample fact"}'

# Read a fact
curl -X GET http://localhost:8000/facts \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001"

# Update a fact
curl -X PUT http://localhost:8000/facts \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001" \
  -H "Content-Type: application/json" \
  -d '{"fact": "Updated fact text"}'

# Delete a fact
curl -X DELETE http://localhost:8000/facts \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001"

# List all facts
curl -X GET http://localhost:8000/facts/all \
  -H "Authorization: Bearer my-secret-token"
```

## Example Usage with curl - Budgets

```bash
# Create a budget
curl -X POST http://localhost:8000/budgets \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001" \
  -H "Content-Type: application/json" \
  -d '{"budget": "Marketing: $5000\nDevelopment: $15000\nInfrastructure: $3000"}'

# Read a budget
curl -X GET http://localhost:8000/budgets \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001"

# Update a budget
curl -X PUT http://localhost:8000/budgets \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001" \
  -H "Content-Type: application/json" \
  -d '{"budget": "Marketing: $6000\nDevelopment: $18000\nInfrastructure: $4000\nDesign: $2000"}'

# Delete a budget
curl -X DELETE http://localhost:8000/budgets \
  -H "Authorization: Bearer my-secret-token" \
  -H "X-Conversation-ID: conv-001"

# List all budgets
curl -X GET http://localhost:8000/budgets/all \
  -H "Authorization: Bearer my-secret-token"
```

## Makefile Commands

```bash
make help      # Show available commands
make build     # Build Docker images
make up        # Start services
make down      # Stop services
make restart   # Restart services
make logs      # Show logs from all services
make logs-api  # Show logs from API service
make logs-db   # Show logs from database service
make test      # Run integration tests
make clean     # Stop services and remove volumes
```

## Database Schema

**Table: facts**

| Column           | Type         | Description                          |
|-----------------|--------------|--------------------------------------|
| conversation_id | VARCHAR(255) | Primary key, conversation identifier |
| fact            | TEXT(16000)  | Large text field for storing facts   |

**Table: budgets**

| Column           | Type          | Description                          |
|-----------------|---------------|--------------------------------------|
| conversation_id | VARCHAR(255)  | Primary key, conversation identifier |
| budget          | TEXT(100000)  | Large text field for storing budgets |

## Environment Variables

- `API_TOKEN`: Bearer token for authentication (default: `CHANGE-THIS-TOKEN-IN-PRODUCTION`)
- `DATABASE_URL`: Database connection string (automatically configured in Docker Compose)
- `MYSQL_ROOT_PASSWORD`: MariaDB root password (default: `rootpassword`)
- `MYSQL_DATABASE`: Database name (default: `perfcons`)
- `MYSQL_USER`: Database user (default: `user`)
- `MYSQL_PASSWORD`: Database password (default: `password`)

**Security Note**: Always change default passwords and tokens in production environments!

## Volume Management

The database data is stored in a named Docker volume: `perfcons-db-data`

To remove the volume and all data:

```bash
make clean
```

## Development

### Running Locally Without Docker

1. Install dependencies:
```bash
pip install -r app/requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URL=mysql+pymysql://user:password@localhost:3306/perfcons
export API_TOKEN=my-secret-token
```

3. Run the application:
```bash
uvicorn app.src.main:app --reload
```

## License

MIT