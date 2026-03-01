from logging.config import fileConfig
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from src.config import Settings

# Import Base without loading db.database (which uses async engine)
import importlib.util
import os
_spec = importlib.util.spec_from_file_location(
    "models",
    os.path.join(os.path.dirname(__file__), "..", "src", "db", "models.py"),
)
_models = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_models)
Base = _models.Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def prepare_database_url(url: str) -> str:
    """Prepare database URL for psycopg2 - remove unsupported params like channel_binding."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    # Remove channel_binding (not supported by psycopg2)
    params.pop("channel_binding", None)
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def get_url() -> str:
    """Get database URL from app config (sync driver for Alembic)."""
    settings = Settings()
    url = settings.database_url
    # Clean URL to remove unsupported params (e.g., channel_binding for Neon)
    return prepare_database_url(url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    config.set_main_option("sqlalchemy.url", get_url())
    configuration = config.get_section(config.config_ini_section, {})
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
