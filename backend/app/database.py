import logging
import time
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_database_session() -> Generator[Session, None, None]:
    database_session = SessionLocal()

    try:
        yield database_session
    finally:
        database_session.close()


def wait_for_database(
    maximum_attempts: int = 20,
    delay_seconds: int = 2,
) -> None:
    for attempt in range(1, maximum_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            logger.info("Database connection successful")
            return

        except Exception as error:
            logger.warning(
                "Database connection attempt %s/%s failed: %s",
                attempt,
                maximum_attempts,
                error,
            )

            if attempt == maximum_attempts:
                raise RuntimeError(
                    "Could not connect to the database"
                ) from error

            time.sleep(delay_seconds)
