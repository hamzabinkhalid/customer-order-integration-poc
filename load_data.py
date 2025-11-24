"""
Load customer and order data from CSV files into the database.
Run this script once to initialize the database with data.
"""
import csv
from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models import Customer, Order


def load_customers(db, csv_file: str = "customers.csv"):
    """Load customer data from CSV file into database."""
    print(f"Loading customers from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        customers = []
        
        for row in reader:
            customer = Customer(
                customer_id=int(row['customer_id']),
                firstname=row['firstname'],
                surname=row['surname'],
                email=row['email'],
                address=row['address'],
                zip_code=row['zip_code'],
                region=row['region'],
                status=row['status']
            )
            customers.append(customer)
        
        db.bulk_save_objects(customers)
        db.commit()
        print(f"Loaded {len(customers)} customers")


def load_orders(db, csv_file: str = "orders.csv"):
    """Load order data from CSV file into database."""
    print(f"Loading orders from {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        orders = []
        
        for row in reader:
            order = Order(
                order_id=int(row['order_id']),
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                customer_id=int(row['customer_id']),
                amount=float(row['amount'])
            )
            orders.append(order)
        
        db.bulk_save_objects(orders)
        db.commit()
        print(f"Loaded {len(orders)} orders")


def main():
    """Main function to create tables and load data."""
    print("Database Initialization")
    print("-" * 60)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Load data
        load_customers(db)
        load_orders(db)
        
        # Verify data
        customer_count = db.query(Customer).count()
        order_count = db.query(Order).count()
        active_count = db.query(Customer).filter(Customer.status == 'active').count()
        archived_count = db.query(Customer).filter(Customer.status == 'archived').count()
        
        print("-" * 60)
        print("Database Statistics:")
        print(f"  Total Customers: {customer_count}")
        print(f"  Active Customers: {active_count}")
        print(f"  Archived Customers: {archived_count}")
        print(f"  Total Orders: {order_count}")
        print("-" * 60)
        print("Database initialization completed successfully")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
