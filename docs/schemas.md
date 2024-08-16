# Schemas

This documentation provides an overview of the available schemas in this package.

Available schemas:

- [BaseModelConfig](#BaseModelConfig)
- [Page Schema](#Page-Schema)

## BaseModelConfig

The `BaseModelConfig` class extends Pydantic's `BaseModel` class and provides
additional configuration settings for models in the application.

The configuration settings include:

- **`alias_generator`**: This configuration uses an `AliasGenerator` to convert field names from snake_case to camelCase. This is useful for APIs where camelCase is the preferred naming convention.
- **`populate_by_name`**: When set to `True`, this allows the model to populate its fields using either the original name or the alias. This is particularly helpful when working with data that might use different naming conventions.

### Usage Example

To use the `BaseModelConfig` class, you can create a new model that inherits from it. Here's an example:

```python
class OwnModel(BaseModelConfig):
    first_name: str
    last_name: str
    full_name: str
```

The fields in your model will be available in snake_case, but when serialized to JSON, they will be converted to camelCase.

- `firstName`
- `lastName`
- `fullName`

### JSON Output Example

Here's an example of the JSON output for the `OwnModel` class:

```json
{
  "firstName": "John",
  "lastName": "Doe",
  "fullName": "John Doe"
}
```

## Page Schema

The `Page` schema can be used when you want to return paginated data. `Page` is a generic schema that can be used with any entity type.

### Fields

- **`items: List[T]`**: A list containing the items on the current page. `T` is a generic type, meaning this can be a list of any entity type.
- **`limit: int`**: The maximum number of items that can be displayed on a single page.
- **`offset: int`**: The starting position of the items on the current page within the entire dataset.
- **`total: int`**: The total number of items across all pages.

### Usage Example

When using the `Page` schema, you can create a paginated response for any entity type. Here's an example of how can use the `Page` schema for a list of `User` entities:

```python
from typing import List

class User(BaseModel):
    id: int
    name: str

# Creating a paginated response for a list of users
user_page = Page[User](
    items=[User(id=1, name="John Doe"), User(id=2, name="Jane Smith")],
    limit=10,
    offset=0,
    total=50
)

print(user_page.json())
```

### JSON Output Example

Here's an example of the JSON output for the `Page` schema:

```json
{
  "items": [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Smith"}
  ],
  "limit": 10,
  "offset": 0,
  "total": 50
}
```
