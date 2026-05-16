import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, engine, is_mystore_configured
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

TEST_DB_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="module")
def api_headers():
    return {"X-API-Key": os.getenv("API_KEY", "your-secret-api-key-change-this")}

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_list_products_no_mystore(client, api_headers):
    if not is_mystore_configured():
        response = client.get("/products", headers=api_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_create_product_no_mystore(client, api_headers):
    if not is_mystore_configured():
        response = client.post("/products", json={"name": "Test", "price": 99.99}, headers=api_headers)
        assert response.status_code == 400

def test_chat_sales_query(client, api_headers):
    response = client.post("/chat", json={"query": "How many orders today?"}, headers=api_headers)
    assert response.status_code == 200
    assert "agent" in response.json()

def test_chat_support_query(client, api_headers):
    response = client.post("/chat", json={"query": "I want a refund for order 1"}, headers=api_headers)
    assert response.status_code == 200
    assert "agent" in response.json()

def test_unauthorized_access(client):
    response = client.get("/products")
    assert response.status_code == 401

def test_create_refund(client, api_headers):
    response = client.post("/refunds", json={"order_id": 1, "customer_name": "Jane Doe", "reason": "Defective product"}, headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Jane Doe"

def test_list_refunds(client, api_headers):
    response = client.get("/refunds", headers=api_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_sales_report(client, api_headers):
    response = client.get("/sales/report?period=daily", headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_orders" in data
    assert "total_revenue" in data

def test_top_products(client, api_headers):
    response = client.get("/sales/top-products", headers=api_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
