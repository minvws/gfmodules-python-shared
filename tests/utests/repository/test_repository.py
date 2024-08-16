from app.model import Person
from app.repository import PersonRepository


class TestRepository:

    def test_create(self, mock_person: Person, repository: PersonRepository) -> None:
        expected_person = mock_person

        repository.create(expected_person)
        actual_person = repository.get(id=expected_person.id)

        assert actual_person == expected_person
