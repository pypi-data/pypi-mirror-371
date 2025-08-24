class TestIntegration:
    def test_health_endpoint(self, test_client):
        """Test the health endpoint"""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "providers" in data
        assert "models" in data

    def test_generate_endpoint(self, test_client):
        """Test the generate endpoint"""
        payload = {
            "prompt": "Test prompt",
            "provider": "custom",
            "model": "test-model",
            "max_tokens": 10,
        }
        response = test_client.post("/api/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert data["provider"] == "custom"

    def test_models_endpoint(self, test_client):
        """Test the models endpoint"""
        response = test_client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        from inferaapi.models import model_registry

        if model_registry.models:
            assert "test-model" in data["models"]
        else:
            assert data["models"] == {}
