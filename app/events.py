"""
Event-driven queue system for order creation events.
Implements a simple in-memory queue with background consumer thread.
"""
import queue
import threading
import json
import os
from datetime import datetime
from typing import Dict, Any
import time


class OrderQueue:
    """Thread-safe queue for order events."""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.running = False
        self.consumer_thread = None
        
    def start_consumer(self):
        """Start the background consumer thread."""
        if not self.running:
            self.running = True
            self.consumer_thread = threading.Thread(target=self._consume_messages, daemon=True)
            self.consumer_thread.start()
    
    def stop_consumer(self):
        """Stop the background consumer thread."""
        self.running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
    
    def publish_order_event(self, order_data: Dict[str, Any]):
        """
        Publish an order creation event to the queue.
        
        Args:
            order_data: Dictionary containing order information
        """
        event = {
            "event_type": "order_created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": order_data
        }
        self.queue.put(event)
    
    def _consume_messages(self):
        """Background thread that consumes messages from the queue."""
        while self.running:
            try:
                # Wait for message with timeout to allow checking running flag
                event = self.queue.get(timeout=1)
                self._process_event(event)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")
    
    def _process_event(self, event: Dict[str, Any]):
        """
        Process an order event by saving it to a file.
        
        Args:
            event: Event dictionary containing order data
        """
        try:
            order_data = event.get("data", {})
            order_id = order_data.get("order_id", "unknown")
            
            # Create output directory if it doesn't exist
            output_dir = "output/orders"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/order_{order_id}_{timestamp}.json"
            
            # Write event to file
            with open(filename, 'w') as f:
                json.dump(event, f, indent=2, default=str)
            
        except Exception as e:
            print(f"Error saving order to file: {e}")


# Global queue instance
order_queue = OrderQueue()


def get_order_queue() -> OrderQueue:
    """Get the global order queue instance."""
    return order_queue
