from sqlalchemy import Engine
from src.gfmodules_python_shared.session.db_session import DbSession


class DbSessionFactory:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create(self) -> DbSession:
        return DbSession(self.engine)
