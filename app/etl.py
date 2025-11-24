"""
ETL (Extract, Transform, Load) job for customer data.
Fetches active customers from API, transforms data, and sends to target endpoint.
"""
import requests
import time
from typing import List, Dict, Any


class CustomerETL:
    """ETL job for processing customer data."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", target_url: str = "https://postman-echo.com/post"):
        self.api_base_url = api_base_url
        self.target_url = target_url
    
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract customer data from the API.
        Fetches all active customers with their orders.
        
        Returns:
            List of customer dictionaries
        """
        print("Extracting active customers from API...")
        
        try:
            response = requests.get(
                f"{self.api_base_url}/customers",
                params={"status": "active"},
                timeout=10
            )
            response.raise_for_status()
            
            customers = response.json()
            print(f"Extracted {len(customers)} active customers")
            return customers
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            raise
    
    def transform(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform customer data by concatenating firstname and surname into name field.
        
        Args:
            customers: List of customer dictionaries
        
        Returns:
            Transformed list of customer dictionaries
        """
        print("Transforming customer data...")
        
        transformed = []
        for customer in customers:
            # Create new customer dict with transformed data
            transformed_customer = {
                "customer_id": customer["customer_id"],
                "name": f"{customer['firstname']} {customer['surname']}",  # Concatenate names
                "email": customer["email"],
                "address": customer["address"],
                "zip_code": customer["zip_code"],
                "region": customer["region"],
                "status": customer["status"],
                "orders": customer.get("orders", [])
            }
            transformed.append(transformed_customer)
        
        print(f"Transformed {len(transformed)} customer records")
        return transformed
    
    def load(self, customers: List[Dict[str, Any]]):
        """
        Load customer data to target API.
        Sends each customer record individually and logs the HTTP response code.
        
        Args:
            customers: List of transformed customer dictionaries
        """
        print(f"Loading {len(customers)} customers to {self.target_url}...")
        
        success_count = 0
        error_count = 0
        
        for i, customer in enumerate(customers, 1):
            try:
                # Send individual customer record to target API
                response = requests.post(
                    self.target_url,
                    json=customer,
                    timeout=10
                )
                
                # Log the HTTP response code
                status_code = response.status_code
                customer_name = customer.get("name", "Unknown")
                
                print(f"[{i}/{len(customers)}] {customer_name}: HTTP {status_code}")
                
                if 200 <= status_code < 300:
                    success_count += 1
                else:
                    error_count += 1
                
                # Small delay to avoid overwhelming the target API
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"[{i}/{len(customers)}] Error sending {customer.get('name')}: {e}")
                error_count += 1
        
        print(f"Summary: {success_count} successful, {error_count} errors")
    
    def run(self):
        """
        Execute the full ETL pipeline.
        Extract -> Transform -> Load
        """
        print("Starting ETL Job")
        print("-" * 60)
        
        try:
            # Extract
            customers = self.extract()
            
            # Transform
            transformed_customers = self.transform(customers)
            
            # Load
            self.load(transformed_customers)
            
            print("-" * 60)
            print("ETL Job completed successfully")
            
        except Exception as e:
            print("-" * 60)
            print(f"ETL Job failed: {e}")
            raise


if __name__ == "__main__":
    # Run ETL job
    etl = CustomerETL()
    etl.run()
