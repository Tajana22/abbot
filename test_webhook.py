from app import app

def test_webhook():
    client = app.test_client()

    response = client.post(
        "/webhook",
        json={"message": "hello"}
    )

    assert response.status_code == 200
