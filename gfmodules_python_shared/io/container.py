from inject import BinderCallable, configure


def setup_container(container: BinderCallable) -> None:
    configure(container, once=True)
