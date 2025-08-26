def test_index(client):
    response = client.get("/")
    assert response.data is not None


def test_playlist(client, mock_yt_api):
    response = client.get("/p/foo")
    assert response.data is not None
    assert response.status_code == 200
    assert "xml" in response.headers["Content-Type"]
    assert "xml" in response.data.decode("utf-8")


def test_channel(client, mock_yt_api):
    response = client.get("/c/foo")
    assert response.data is not None
    assert response.status_code == 200
    assert "xml" in response.headers["Content-Type"]
    assert "xml" in response.data.decode("utf-8")


def test_user(client, mock_yt_api):
    response = client.get("/u/foo")
    assert response.data is not None
    assert response.status_code == 200
    assert "xml" in response.headers["Content-Type"]
    assert "xml" in response.data.decode("utf-8")


def test_404(client):
    response = client.get("/foo")
    assert response.data is not None
    assert response.status_code == 200
    assert "xml" in response.headers["Content-Type"]
    assert "xml" in response.data.decode("utf-8")
