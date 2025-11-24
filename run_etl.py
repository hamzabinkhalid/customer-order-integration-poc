"""
ETL Job Runner
Execute this script to run the ETL job that processes customer data.
Ensure the API is running before executing this script.
"""
from app.etl import CustomerETL
import sys


def main():
    """Run the ETL job."""
    # Create and run ETL job
    etl = CustomerETL(
        api_base_url="http://localhost:8000",
        target_url="https://postman-echo.com/post"
    )
    
    try:
        etl.run()
        return 0
    except Exception as e:
        print(f"\nETL job failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure the API is running: python main.py")
        print("  2. Check database is initialized: python load_data.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
