import requests

def test_login():
    url = "http://localhost:8000/auth/login"
    payload = {
        "email": "najat@optistock.ma",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
