"""
SQLAlchemy ORM models for Customer and Order tables.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    """Customer model representing customer data from CSV."""
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    region = Column(String, nullable=False)
    status = Column(String, nullable=False)  # 'active' or 'archived'

    # Relationship to orders
    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name={self.firstname} {self.surname})>"


class Order(Base):
    """Order model representing order data from CSV."""
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    amount = Column(Float, nullable=False)

    # Relationship to customer
    customer = relationship("Customer", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.order_id}, customer_id={self.customer_id}, amount={self.amount})>"
