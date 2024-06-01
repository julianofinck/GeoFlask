def test_ping(client):
    response = client.get("/ping")

    assert response.status_code == 200
    print(response.data)
    assert b"pong" in response.data
