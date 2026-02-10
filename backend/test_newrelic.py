#!/usr/bin/env python3
"""
Test script to verify New Relic agent is working correctly.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, '/Users/sahilsingh/Desktop/GoComet/backend')

os.environ['NEW_RELIC_CONFIG_FILE'] = '/Users/sahilsingh/Desktop/GoComet/backend/newrelic.ini'

print("=" * 60)
print("NEW RELIC AGENT DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Check if config file exists
config_path = '/Users/sahilsingh/Desktop/GoComet/backend/newrelic.ini'
print(f"\n✓ Test 1: Checking config file...")
if os.path.exists(config_path):
    print(f"  ✓ Config file found: {config_path}")
    with open(config_path, 'r') as f:
        print(f"  Content:\n{f.read()}\n")
else:
    print(f"  ✗ Config file NOT found: {config_path}")
    sys.exit(1)

# Test 2: Import New Relic
print("✓ Test 2: Importing New Relic agent...")
try:
    import newrelic.agent
    print("  ✓ New Relic agent imported successfully")
except ImportError as e:
    print(f"  ✗ Failed to import: {e}")
    sys.exit(1)

# Test 3: Initialize agent
print("✓ Test 3: Initializing New Relic agent...")
try:
    newrelic.agent.initialize(config_path)
    print("  ✓ Agent initialized successfully")
except Exception as e:
    print(f"  ✗ Initialization failed: {e}")
    sys.exit(1)

# Test 4: Check agent status
print("✓ Test 4: Checking agent status...")
try:
    from newrelic.agent import get_agent
    agent = get_agent()
    print(f"  ✓ Agent active: {agent._is_valid}")
    print(f"  ✓ App name: {agent._app_name}")
    print(f"  ✓ License key (first 10 chars): {agent._license_keys[0][:10] if agent._license_keys else 'NOT SET'}...")
except Exception as e:
    print(f"  ✗ Status check failed: {e}")

# Test 5: Make a test call
print("✓ Test 5: Recording test transaction...")
try:
    @newrelic.agent.function_trace()
    def test_function():
        return "test_success"
    
    transaction = newrelic.agent.current_transaction()
    if transaction:
        print(f"  ✓ Currently in transaction: {transaction}")
    
    result = test_function()
    print(f"  ✓ Test function executed: {result}")
except Exception as e:
    print(f"  ✗ Transaction test failed: {e}")

print("\n" + "=" * 60)
print("✅ NEW RELIC DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nIf all tests passed, New Relic should be working.")
print("Wait 2-5 minutes, then check: https://one.newrelic.com/")
print("Look for 'GoComet-Backend' under APM → All Applications")
