from inferaapi.config import Settings


def test_settings_defaults():
    """Test that settings have correct defaults"""
    settings = Settings()
    assert settings.app_name == "inferaAPI"
    assert settings.port == 8000
    assert settings.host == "0.0.0.0"


def test_settings_env_vars(monkeypatch):
    """Test that settings read environment variables"""
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("DEBUG", "true")

    settings = Settings()
    assert settings.openai_api_key == "test_key"
    assert settings.debug is True
