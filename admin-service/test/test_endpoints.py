import app

def test_admin_videos(monkeypatch):
    class MockResponse:
        status_code = 200
        content = b'[{"title": "Fake Video", "id": 99, "duration": 999, "description": "Test"}]'

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    client = app.app.test_client()
    response = client.get("/admin/videos")
    assert response.status_code == 200
    assert b"Fake Video" in response.data