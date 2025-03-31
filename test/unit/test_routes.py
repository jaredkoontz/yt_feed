def test_index(client):
    response = client.get("/")
    assert response.data is not None
