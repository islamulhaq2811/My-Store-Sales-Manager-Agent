# Sales Manager Agent

AI-powered Sales Manager Agent built with Python + FastAPI, based on the Business Manager Agent plan.

## Features

- **Master Agent**: Routes queries to appropriate specialized agents
- **Sales Agent**: Daily orders, revenue, sales reports, top products
- **Support Agent**: FAQs, refunds, warranty, delivery status
- **REST API**: FastAPI endpoints for all operations
- **MySQL Database**: Persistent storage for products, orders, sales logs

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create MySQL database:
```sql
CREATE DATABASE sales_manager;
```

3. Initialize database tables:
```bash
python init_db.py
```

4. Run the server:
```bash
python -m uvicorn main:app --reload
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Master Agent chat interface |
| `/products` | POST | Create a product |
| `/products` | GET | List all products |
| `/orders` | POST | Create an order |
| `/orders/today` | GET | Get today's orders |
| `/sales/report` | GET | Get sales report (daily/weekly/monthly) |
| `/sales/top-products` | GET | Get top selling products |

## Example Usage

```bash
# Create a product
curl -X POST "http://localhost:8000/products" -H "Content-Type: application/json" -d '{"name": "iPhone Cable", "price": 25.99, "category": "Electronics"}'

# Create an order
curl -X POST "http://localhost:8000/orders" -H "Content-Type: application/json" -d '{"customer_name": "John Doe", "product_id": 1, "quantity": 2}'

# Chat with Master Agent
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"query": "How many orders today?"}'

# Get sales report
curl "http://localhost:8000/sales/report?period=daily"
```
