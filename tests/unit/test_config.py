from prometheus.config import settings

def test_config_defaults():
    assert settings.ENV in ["development", "staging", "production"]
    assert settings.LOG_LEVEL is not None
