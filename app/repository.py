from src.gfmodules_python_shared.repository.repository_base import RepositoryBase
from src.gfmodules_python_shared.session.db_session import DbSession

from app.model import Person


class PersonRepository(RepositoryBase[Person]):

    def __init__(self, db_session: DbSession) -> None:
        super().__init__(db_session, Person)