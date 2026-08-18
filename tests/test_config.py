from amesh.config import Settings


def test_reference_configuration_is_postgresql_only() -> None:
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert not hasattr(settings, "nats_url")
    assert settings.object_storage_bucket == "amesh"
