#!/usr/bin/env python3
"""Check if New Relic license key format is valid"""

license_key = "067E76400B384FCBFB1A6FC9206500255253F5B89837CC0D83C9F1CD6D294870"

print(f"License Key: {license_key}")
print(f"Length: {len(license_key)} characters")
print(f"Expected length: 40 characters")

if len(license_key) == 40:
    print("✓ Length is correct")
else:
    print(f"✗ INVALID LENGTH! Should be 40, got {len(license_key)}")

# Check if all characters are hex
if all(c in '0123456789ABCDEFabcdef' for c in license_key):
    print("✓ All characters are valid hex")
else:
    print("✗ Contains non-hex characters")

print("\n🔑 YOUR LICENSE KEY APPEARS TO BE INVALID!")
print("\nTo fix this:")
print("1. Go to: https://one.newrelic.com/api-keys")
print("2. Create a NEW INGEST LICENSE KEY (not USER API KEY)")
print("3. Copy the 40-character key")
print("4. Update newrelic.ini with the correct key")
print("5. Restart the backend server")
print("6. Run generate_data.py again")
