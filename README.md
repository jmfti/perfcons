# Perfcons - Facts and Budgets Management API

A REST API built with FastAPI and MariaDB for managing facts and budgets associated with conversation IDs.

## Features

- **FastAPI** REST API with automatic Swagger documentation
- **MariaDB** database with named volume for data persistence
- **Bearer Token Authentication** for secure API access
- **CRUD Operations** for facts and budgets associated with conversation IDs
- **Integration Tests** with unittest
- **Docker Compose** stack for easy deployment
- **Large Text Support** - Facts can store up to 16,000 characters, budgets can store up to 100,000 characters
- **ngrok Integration** - Expose your API to the internet for testing and sharing

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
ngrok web interface at `http://localhost:4040` (to inspect requests and get the public URL)

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
NGROK_AUTHTOKEN=your-ngrok-authtoken-here
```

**Important**: For production deployments, always change the default passwords and API token!

**ngrok Setup (Required for internet access)**: To expose your API to the internet via ngrok:
1. Sign up for a free account at [ngrok.com](https://ngrok.com)
2. Get your authtoken from [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
3. Add the authtoken to your `.env` file as `NGROK_AUTHTOKEN`
4. Restart the services with `make restart`

**Note**: ngrok requires an authtoken to create tunnels. Without it, the ngrok service will show authentication errors in the logs but other services (API and DB) will work normally.

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

All endpoints require Bearer token authentication via the `Authorization` header. Endpoints that operate on specific conversation data require the conversation ID as a URL path parameter (except `/facts/all`, `/budgets/all` and `/health`).

### Authentication

```
Authorization: Bearer <your-api-token>
```

### Create Fact

```bash
POST /facts/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
Body:
  {
    "fact": "Your fact text here"
  }
```

### Read Fact

```bash
GET /facts/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
```

### Update Fact

```bash
PUT /facts/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
Body:
  {
    "fact": "Updated fact text"
  }
```

### Delete Fact

```bash
DELETE /facts/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
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
POST /budgets/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
Body:
  {
    "budget": "Your budget text here"
  }
```

### Read Budget

```bash
GET /budgets/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
```

### Update Budget

```bash
PUT /budgets/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
Body:
  {
    "budget": "Updated budget text"
  }
```

### Delete Budget

```bash
DELETE /budgets/{conversation_id}
Headers:
  Authorization: Bearer my-secret-token
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
curl -X POST http://localhost:8000/facts/conv-001 \
  -H "Authorization: Bearer my-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"fact": "This is a sample fact"}'

# Read a fact
curl -X GET http://localhost:8000/facts/conv-001 \
  -H "Authorization: Bearer my-secret-token"

# Update a fact
curl -X PUT http://localhost:8000/facts/conv-001 \
  -H "Authorization: Bearer my-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"fact": "Updated fact text"}'

# Delete a fact
curl -X DELETE http://localhost:8000/facts/conv-001 \
  -H "Authorization: Bearer my-secret-token"

# List all facts
curl -X GET http://localhost:8000/facts/all \
  -H "Authorization: Bearer my-secret-token"
```

## Example Usage with curl - Budgets

```bash
# Create a budget
curl -X POST http://localhost:8000/budgets/conv-001 \
  -H "Authorization: Bearer my-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"budget": "Marketing: $5000\nDevelopment: $15000\nInfrastructure: $3000"}'

# Read a budget
curl -X GET http://localhost:8000/budgets/conv-001 \
  -H "Authorization: Bearer my-secret-token"

# Update a budget
curl -X PUT http://localhost:8000/budgets/conv-001 \
  -H "Authorization: Bearer my-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"budget": "Marketing: $6000\nDevelopment: $18000\nInfrastructure: $4000\nDesign: $2000"}'

# Delete a budget
curl -X DELETE http://localhost:8000/budgets/conv-001 \
  -H "Authorization: Bearer my-secret-token"

# List all budgets
curl -X GET http://localhost:8000/budgets/all \
  -H "Authorization: Bearer my-secret-token"
```

## Makefile Commands

```bash
make help        # Show available commands
make build       # Build Docker images
make up          # Start services
make down        # Stop services
make restart     # Restart services
make logs        # Show logs from all services
make logs-api    # Show logs from API service
make logs-db     # Show logs from database service
make logs-ngrok  # Show logs from ngrok service
make ngrok-url   # Get the ngrok public URL for internet access
make test        # Run integration tests
make clean       # Stop services and remove volumes
```

## Using ngrok for Internet Access

The ngrok service creates a secure tunnel to expose your local API to the internet. This is useful for:
- Testing webhooks
- Sharing your development API with others
- Testing from mobile devices
- Integration with external services

### Get your ngrok public URL

After starting the services with `make up`, get your public URL:

```bash
make ngrok-url
```

This will output something like: `https://abc123.ngrok.io`

You can also:
- Visit `http://localhost:4040` in your browser to see the ngrok web interface
- Inspect all HTTP requests and responses in real-time
- Replay requests for debugging

### Example: Using the API through ngrok

```bash
# Get your ngrok URL (will output just the URL when tunnel is ready)
make ngrok-url

# Or store it in a variable for use in commands
# Note: Redirect stderr to suppress any Make process messages
NGROK_URL=$(make ngrok-url 2>&1 | grep "https://")

# Create a fact through the internet
curl -X POST ${NGROK_URL}/facts/conv-001 \
  -H "Authorization: Bearer my-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"fact": "Testing through ngrok!"}'
```

### ngrok Web Interface

Visit `http://localhost:4040` to access the ngrok inspection interface where you can:
- See the public URL assigned to your tunnel
- View all HTTP requests and responses
- Replay requests
- See request/response details and timing

## Database Schema

**Table: facts**

| Column           | Type         | Description                              |
|-----------------|--------------|------------------------------------------|
| conversation_id | VARCHAR(255) | Primary key, conversation identifier     |
| fact            | TEXT         | Text field for storing facts (up to 16,000 characters) |

**Table: budgets**

| Column           | Type          | Description                              |
|-----------------|---------------|------------------------------------------|
| conversation_id | VARCHAR(255)  | Primary key, conversation identifier     |
| budget          | TEXT          | Text field for storing budgets (up to 100,000 characters) |

## Environment Variables

- `API_TOKEN`: Bearer token for authentication (default: `CHANGE-THIS-TOKEN-IN-PRODUCTION`)
- `DATABASE_URL`: Database connection string (automatically configured in Docker Compose)
- `MYSQL_ROOT_PASSWORD`: MariaDB root password (default: `rootpassword`)
- `MYSQL_DATABASE`: Database name (default: `perfcons`)
- `MYSQL_USER`: Database user (default: `user`)
- `MYSQL_PASSWORD`: Database password (default: `password`)
- `NGROK_AUTHTOKEN`: (Required for ngrok) Your ngrok authentication token for creating internet tunnels. Get it from https://dashboard.ngrok.com/get-started/your-authtoken

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