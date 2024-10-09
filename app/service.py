from uuid import UUID

from gfmodules_python_shared.session.session_manager import (
    get_repository,
    session_manager,
)

from .model import Person
from .repository import PersonRepository


class PersonService:
    @session_manager
    def get_one(
        self, person_id: UUID, person_repository: PersonRepository = get_repository()
    ) -> Person:
        return person_repository.get_or_fail(id=person_id)
