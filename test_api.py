import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    endpoints = [
        "/health",
        "/api/v1/feed/live",
        "/api/v1/narratives/clusters",
        "/api/v1/sources/credibility"
    ]
    
    for ep in endpoints:
        url = base_url + ep
        try:
            print(f"Testing {url}...", end=" ")
            res = requests.get(url)
            print(f"Status: {res.status_code}")
            if res.status_code != 200:
                print(f"Response: {res.text}")
            else:
                data = res.json()
                print(f"Data keys: {list(data.keys())}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
