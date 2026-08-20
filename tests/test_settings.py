from packages.config.settings import get_settings


def test_settings_load_from_environment() -> None:
    settings = get_settings()

    assert settings.app_name == "Job Application Agent"
    assert settings.app_env == "development"
    assert settings.mysql_host == "127.0.0.1"
    assert settings.mysql_port == 3307
    assert settings.mysql_database == "job_application_agent"
