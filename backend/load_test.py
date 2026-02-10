#!/usr/bin/env python3
"""
Simple load generator to create monitoring data for New Relic.
Makes HTTP requests to the backend health endpoint.
"""
import random
import time
from datetime import datetime

import requests

BACKEND_URL = "http://localhost:8000"
ENDPOINTS = [
    "/health",
    "/",
]

def make_requests(duration_seconds=60, interval=2):
    """
    Make requests to the backend for monitoring purposes.
    
    Args:
        duration_seconds: How long to run (default 60 seconds)
        interval: Delay between requests in seconds (default 2)
    """
    start_time = time.time()
    request_count = 0
    
    print(f"🚀 Load test starting at {datetime.now()}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Interval: {interval} seconds between requests\n")
    
    while time.time() - start_time < duration_seconds:
        endpoint = random.choice(ENDPOINTS)
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            response = requests.get(url, timeout=5)
            request_count += 1
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {request_count:3d} GET {endpoint:15s} -> {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
            
            # Occasionally make a slow request to trigger New Relic alerts
            if random.random() < 0.1:
                time.sleep(0.5)
                
        except Exception as e:
            print(f"✗ {request_count + 1:3d} GET {endpoint:15s} -> ERROR: {str(e)[:50]}")
        
        time.sleep(interval)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Load test completed at {datetime.now()}")
    print(f"Total requests: {request_count}")
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"Requests/sec: {request_count / elapsed:.2f}")

if __name__ == "__main__":
    try:
        # Run for 2 minutes, making a request every 2 seconds
        make_requests(duration_seconds=120, interval=2)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
