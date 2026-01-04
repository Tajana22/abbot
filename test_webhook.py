import requests
import json

url = "http://127.0.0.1:5000/webhook"
data = {
    "message": {
        "chat": {"id": 123456789},
        "from": {"username": "testuser"},
        "text": "Привіт, бот!"
    }
}

response = requests.post(url, json=data)
print(response.text)

