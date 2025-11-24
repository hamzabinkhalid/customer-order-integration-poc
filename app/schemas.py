"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import date


class OrderBase(BaseModel):
    """Base schema for Order data."""
    date: date
    customer_id: int
    amount: float = Field(..., gt=0, description="Order amount must be greater than 0")


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    pass


class OrderResponse(OrderBase):
    """Schema for Order response."""
    order_id: int
    
    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    """Base schema for Customer data."""
    customer_id: int
    firstname: str
    surname: str
    email: str
    address: str
    zip_code: str
    region: str
    status: str


class CustomerWithOrders(CustomerBase):
    """Schema for Customer response including all orders."""
    orders: List[OrderResponse] = []

    model_config = ConfigDict(from_attributes=True)
