def test_generate_endpoint(test_client):
    """Test the generate endpoint"""
    response = test_client.post(
        "/api/generate",
        json={"prompt": "Hello", "provider": "custom", "model": "test-model", "max_tokens": 10},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"].startswith("Test response to: Hello")
    assert data["provider"] == "custom"
    assert data["model"] == "test-model"


def test_health_endpoint(test_client):
    """Test the health endpoint"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "providers" in data
    assert "models" in data
