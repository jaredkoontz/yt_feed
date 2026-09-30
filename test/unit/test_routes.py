def test_index(client):
    response = client.get("/")
    assert response.data is not None
    assert response.status_code == 200


def test_index_converts_pasted_url(client):
    response = client.get("/", query_string={"url": "https://youtube.com/@AdamNeely"})
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert '/c/@AdamNeely"' in body
    assert 'id="feed_url"' in body
    assert "Couldn't find" not in body


def test_index_rejects_unknown_url(client):
    response = client.get("/", query_string={"url": "https://example.com"})
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "Couldn't find a channel" in body
    assert 'id="feed_url"' not in body


def test_index_escapes_pasted_url(client):
    response = client.get("/", query_string={"url": '"><script>alert(1)</script>'})
    body = response.data.decode("utf-8")
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body


def test_404(client):
    response = client.get("/foo")
    assert response.status_code == 404
    assert "404" in response.data.decode("utf-8")


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
