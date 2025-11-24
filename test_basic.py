"""
Minimal functional tests for Customer Order Integration POC.
Tests basic functionality of all 4 tasks.

Run with: pytest test_basic.py -v
"""
import pytest
from datetime import date
from app.database import SessionLocal, engine, Base
from app.models import Customer, Order
from app.schemas import OrderCreate, CustomerWithOrders


class TestTask1Database:
    """Test Task 1: Database creation and CSV loading."""
    
    def test_database_has_customers(self):
        """Verify customers are loaded in database."""
        db = SessionLocal()
        try:
            customer_count = db.query(Customer).count()
            assert customer_count == 10, "Should have 10 customers"
        finally:
            db.close()
    
    def test_database_has_orders(self):
        """Verify orders are loaded in database."""
        db = SessionLocal()
        try:
            order_count = db.query(Order).count()
            assert order_count >= 100, "Should have at least 100 orders"
        finally:
            db.close()
    
    def test_customer_order_relationship(self):
        """Verify customer-order relationship works."""
        db = SessionLocal()
        try:
            customer = db.query(Customer).first()
            assert customer is not None
            assert hasattr(customer, 'orders')
            assert len(customer.orders) > 0, "Customer should have orders"
        finally:
            db.close()


class TestTask2API:
    """Test Task 2: REST API endpoints."""
    
    def test_get_all_customers(self):
        """Test GET /customers endpoint."""
        from fastapi.testclient import TestClient
        from app.api import app
        
        client = TestClient(app)
        response = client.get("/customers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_active_customers(self):
        """Test GET /customers?status=active."""
        from fastapi.testclient import TestClient
        from app.api import app
        
        client = TestClient(app)
        response = client.get("/customers?status=active")
        assert response.status_code == 200
        data = response.json()
        for customer in data:
            assert customer['status'] == 'active'
    
    def test_get_single_customer(self):
        """Test GET /customers/{id}."""
        from fastapi.testclient import TestClient
        from app.api import app
        
        client = TestClient(app)
        response = client.get("/customers/1")
        assert response.status_code == 200
        data = response.json()
        assert data['customer_id'] == 1
        assert 'orders' in data
    
    def test_create_order(self):
        """Test POST /orders."""
        from fastapi.testclient import TestClient
        from app.api import app
        
        client = TestClient(app)
        order_data = {
            "date": "2024-01-23",
            "customer_id": 1,
            "amount": 99.99
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        data = response.json()
        assert data['customer_id'] == 1
        assert data['amount'] == 99.99
        assert 'order_id' in data


class TestTask3ETL:
    """Test Task 3: ETL job functionality."""
    
    def test_etl_extract(self):
        """Test ETL extract phase."""
        from app.etl import CustomerETL
        
        etl = CustomerETL()
        customers = etl.extract()
        assert isinstance(customers, list)
        assert len(customers) > 0
    
    def test_etl_transform(self):
        """Test ETL transform phase (name concatenation)."""
        from app.etl import CustomerETL
        
        etl = CustomerETL()
        sample_data = [{
            "customer_id": 1,
            "firstname": "John",
            "surname": "Doe",
            "email": "john@example.com",
            "address": "123 Main St",
            "zip_code": "12345",
            "region": "Region",
            "status": "active",
            "orders": []
        }]
        
        transformed = etl.transform(sample_data)
        assert transformed[0]['name'] == "John Doe"
        assert 'firstname' not in transformed[0]
        assert 'surname' not in transformed[0]


class TestTask4Events:
    """Test Task 4: Event-driven queue system."""
    
    def test_queue_initialization(self):
        """Test that queue can be initialized."""
        from app.events import OrderQueue
        
        queue = OrderQueue()
        assert queue.queue is not None
        assert queue.running == False
    
    def test_event_publishing(self):
        """Test publishing an order event."""
        from app.events import OrderQueue
        
        queue = OrderQueue()
        order_data = {
            "order_id": 999,
            "date": "2024-01-23",
            "customer_id": 1,
            "amount": 99.99,
            "customer_name": "Test Customer"
        }
        
        queue.publish_order_event(order_data)
        assert not queue.queue.empty()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
