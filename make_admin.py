import requests
import os
import sys

# Load env manually or assume defaults
# We need API_KEY. It is in .env usually.
# Let's try to read .env
API_KEY = None
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY="):
                API_KEY = line.strip().split("=", 1)[1]
                break
except:
    pass

if not API_KEY:
    print("Error: Could not find API_KEY in .env")
    print("Please ensure you are running this in the distrowiki-api directory and .env exists.")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python make_admin.py <email>")
    sys.exit(1)

email = sys.argv[1]
url = "http://localhost:8000/community/admin/promote"

print(f"Promoting {email} to admin...")

try:
    response = requests.post(
        url,
        json={"email": email},
        headers={"X-API-Key": API_KEY}
    )
    
    if response.status_code == 200:
        print("Success!", response.json())
    else:
        print(f"Failed (HTTP {response.status_code}):", response.text)

except Exception as e:
    print(f"Connection error: {e}")
    print("Make sure the API server is running at http://localhost:8000")
