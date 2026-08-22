from packages.config.settings import Settings


def test_greenhouse_settings_load_from_environment() -> None:
    settings = Settings(
        mysql_host="localhost",
        mysql_port=3306,
        mysql_database="job_agent",
        mysql_user="root",
        mysql_password="password",
        greenhouse_enabled=True,
        greenhouse_board_tokens="company1,company2",
    )

    assert settings.greenhouse_enabled is True
    assert settings.greenhouse_board_tokens == "company1,company2"
