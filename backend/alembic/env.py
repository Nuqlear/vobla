import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine



sys.path.append(os.getcwd())
from vobla.db import metadata as target_metadata
config = context.config
if config.attributes.get('configure_logger', True):
    fileConfig(config.config_file_name)


def get_url():
    from vobla.settings import config

    return "postgresql://%s:%s@%s/%s" % (
        config['postgres']['user'],
        config['postgres']['password'],
        config['postgres']['host'],
        config['postgres']['db'],
    )


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(get_url())

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
