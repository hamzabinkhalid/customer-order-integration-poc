# Customer Order Integration POC

A proof-of-concept implementation demonstrating database management, REST API development, ETL integration, and event-driven architecture for customer order processing.

## Overview

This project implements four core tasks:

1. **Database Setup** - Load customer and order data from CSV files into SQLite
2. **REST API** - Three endpoints for customer/order management
3. **ETL Pipeline** - Scheduled job for data transformation and external API integration
4. **Event System** - Queue-based order processing with file output

## Technology Stack

- **Framework**: FastAPI 0.115.0
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic 2.10.3
- **Server**: Uvicorn 0.32.1
- **Testing**: pytest 7.4.3

## Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Initialization

```bash
python load_data.py
```

Loads 10 customers and 100 orders from CSV files into SQLite database.

### Running the API

```bash
python main.py
```

API runs on `http://localhost:8000`

Documentation available at `http://localhost:8000/docs`

### Running Tests

```bash
pytest test_basic.py -v
```

## API Endpoints

### GET /customers

List all customers with their orders. Supports optional status filtering.

**Parameters:**
- `status` (optional): Filter by "active" or "archived"

**Example:**
```bash
curl http://localhost:8000/customers?status=active
```

### GET /customers/{customer_id}

Retrieve a single customer by ID with their order history.

**Example:**
```bash
curl http://localhost:8000/customers/1
```

### POST /orders

Create a new order for an existing customer.

**Request Body:**
```json
{
  "date": "2024-01-23",
  "customer_id": 1,
  "amount": 99.99
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-01-23", "customer_id": 1, "amount": 99.99}'
```

## ETL Job

The ETL pipeline fetches active customers, transforms data by concatenating names, and sends records to an external API.

### Running the ETL

```bash
python run_etl.py
```

**Note**: API must be running before executing the ETL job.

### Process

1. **Extract**: Fetch active customers from local API
2. **Transform**: Concatenate `firstname` + `surname` into `name` field
3. **Load**: POST each customer to `postman-echo.com`
4. **Logging**: HTTP response codes logged for each request

## Event-Driven System

Order creation events are automatically queued and processed in the background. Each event is saved as a JSON file.

### Implementation

- Thread-safe in-memory queue
- Background consumer thread
- Automatic lifecycle management
- Output saved to `output/orders/`

### Event File Format

```json
{
  "event_type": "order_created",
  "timestamp": "2024-01-23T10:30:00.000000",
  "data": {
    "order_id": 101,
    "date": "2024-01-23",
    "customer_id": 1,
    "amount": 99.99,
    "customer_name": "John Doe"
  }
}
```

## Project Structure

```
.
├── app/
│   ├── __init__.py       # Package initialization
│   ├── api.py            # FastAPI application and endpoints
│   ├── database.py       # Database configuration
│   ├── etl.py            # ETL pipeline implementation
│   ├── events.py         # Event queue system
│   ├── models.py         # SQLAlchemy ORM models
│   └── schemas.py        # Pydantic validation schemas
├── customers.csv         # Customer source data
├── orders.csv            # Order source data
├── load_data.py          # Database initialization script
├── main.py               # Application entry point
├── run_etl.py            # ETL job runner
├── test_basic.py         # Functional tests
└── requirements.txt      # Python dependencies
```
