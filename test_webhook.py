from main import app

def test_webhook():
    client = app.test_client()

    response = client.post(
        "/webhook",
        json={
            "message": {
                "chat": {"id": 123},
                "from": {"username": "test_user"},
                "text": "hello"
            }
        }
    )

    assert response.status_code == 200
