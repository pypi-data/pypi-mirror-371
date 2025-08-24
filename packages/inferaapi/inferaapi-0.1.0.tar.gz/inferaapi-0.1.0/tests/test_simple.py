def test_imports():
    """Test that all modules can be imported"""
    from inferaapi import app, settings
    from inferaapi.models import model_registry

    assert app is not None
    assert settings is not None
    assert model_registry is not None


def test_config():
    """Test configuration loading"""
    from inferaapi.config import settings

    assert hasattr(settings, "app_name")
    assert hasattr(settings, "port")
    assert settings.app_name == "inferaAPI"


def test_app_creation():
    """Test that the app can be created"""
    from inferaapi.app import app

    assert app is not None
    assert hasattr(app, "routes")
