import logging

import inject
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)


def is_healthy_database() -> bool:
    session_maker = inject.instance(sessionmaker[Session])
    try:
        with session_maker.begin() as session:
            return bool(session.execute(text("SELECT 1")))

    except Exception as e:
        logger.info(f"Database is not healthy: {e}")
        return False
