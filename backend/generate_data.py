#!/usr/bin/env python3
import time
import urllib.request
from datetime import datetime

print("🚀 Starting load test...")
print(f"Time: {datetime.now()}\n")

start = time.time()
count = 0

for i in range(60):  # 60 requests with 2-second interval = 2 minutes
    try:
        req_start = time.time()
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
        elapsed = time.time() - req_start
        count += 1
        print(f"✓ {count:2d} GET /health -> 200 ({elapsed:.3f}s)")
        response.close()
    except Exception as e:
        print(f"✗ Request {i+1} failed: {str(e)[:40]}")
    
    time.sleep(2)  # Wait 2 seconds between requests

total_time = time.time() - start
print(f"\n✅ Test complete!")
print(f"Requests sent: {count}")
print(f"Time elapsed: {total_time:.1f}s")
print(f"\n📊 Data should appear in New Relic APM within 1-5 minutes")
