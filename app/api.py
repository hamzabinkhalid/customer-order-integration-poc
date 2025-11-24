"""
FastAPI REST API with three endpoints:
1. GET /customers - Get all customers (with optional status filter)
2. GET /customers/{customer_id} - Get single customer
3. POST /orders - Create new order
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager

from app.database import get_db, engine, Base
from app.models import Customer, Order
from app.schemas import CustomerWithOrders, OrderCreate, OrderResponse
from app.events import get_order_queue

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Start the order event consumer
    queue = get_order_queue()
    queue.start_consumer()
    
    yield
    
    # Shutdown: Stop the order event consumer
    queue.stop_consumer()


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Customer Order Integration API",
    description="REST API for managing customers and orders",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/customers", response_model=List[CustomerWithOrders], tags=["Customers"])
def get_customers(
    status: Optional[str] = Query(None, description="Filter by status: 'active' or 'archived'"),
    db: Session = Depends(get_db)
):
    """
    Get all customers with their orders.
    
    Query Parameters:
        - status: Optional filter for 'active' or 'archived' customers
    
    Returns:
        List of customers with their associated orders
    """
    query = db.query(Customer)
    
    # Apply status filter if provided
    if status:
        if status not in ["active", "archived"]:
            raise HTTPException(
                status_code=400,
                detail="Status must be 'active' or 'archived'"
            )
        query = query.filter(Customer.status == status)
    
    customers = query.all()
    return customers


@app.get("/customers/{customer_id}", response_model=CustomerWithOrders, tags=["Customers"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Get a single customer by ID with their orders.
    
    Path Parameters:
        - customer_id: The customer's unique identifier
    
    Returns:
        Customer data with associated orders
    
    Raises:
        404: Customer not found
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {customer_id} not found"
        )
    
    return customer


@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    
    Request Body:
        - date: Order date (YYYY-MM-DD)
        - customer_id: ID of the customer placing the order
        - amount: Order amount (must be > 0)
    
    Returns:
        Created order data
    
    Raises:
        404: Customer not found
        400: Invalid order data
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.customer_id == order.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {order.customer_id} not found"
        )
    
    # Create new order
    db_order = Order(
        date=order.date,
        customer_id=order.customer_id,
        amount=order.amount
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Publish order creation event to queue
    queue = get_order_queue()
    order_data = {
        "order_id": db_order.order_id,
        "date": str(db_order.date),
        "customer_id": db_order.customer_id,
        "amount": db_order.amount,
        "customer_name": f"{customer.firstname} {customer.surname}"
    }
    queue.publish_order_event(order_data)
    
    return db_order
