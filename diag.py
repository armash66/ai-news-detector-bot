import urllib.request
import json
import sys

def test_api():
    base_url = "http://localhost:8000"
    endpoints = [
        "/health",
        "/api/v1/feed/live"
    ]
    
    for ep in endpoints:
        url = base_url + ep
        try:
            print(f"Testing {url}...")
            with urllib.request.urlopen(url) as response:
                status = response.getcode()
                body = response.read().decode('utf-8')
                print(f"  Status: {status}")
                print(f"  Body: {body[:100]}")
        except urllib.error.HTTPError as e:
            print(f"  HTTP Error {e.code}: {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_api()
