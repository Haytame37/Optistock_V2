import requests

url = "https://demo.thingsboard.io/api/v1/A5nfCs8VOOzz97F0sD4h/telemetry"
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
