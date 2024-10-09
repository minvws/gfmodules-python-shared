from gfmodules_python_shared.schema.sql_model import TSQLModel


def are_the_same_entity(actual: TSQLModel, comparer: TSQLModel) -> bool:
    return all(
        getattr(actual, key) == getattr(comparer, key)
        for key in actual.__table__.columns.keys()  # noqa: SIM118
    )
