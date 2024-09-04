from typing import Type
from gfmodules_python_shared.repository.base import RepositoryBase

from app.model import Person


class PersonRepository(RepositoryBase[Person]):
    model: Type[Person] = Person
