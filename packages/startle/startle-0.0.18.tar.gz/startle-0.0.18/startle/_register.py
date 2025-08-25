from typing import Any, Callable


def register(
    type_: type,
    parser: Callable[[str], Any] | None = None,
    metavar: str | list[str] | None = None,
) -> None:
    """
    Register a custom parser and metavar for a type.
    `parser` can be omitted to specify a custom metavar for an already parsable type.

    Args:
        type_: The type to register the parser and metavar for.
        parser: A function that takes a string and returns a value of the type.
        metavar: The metavar to use for the type in the help message.
            If None, default metavar "val" is used.
            If list, the metavar is treated as a literal list of possible choices,
            such as ["true", "false"] yielding "true|false" for a boolean type.
    """
    # TODO: should overwrite be disallowed?

    from .metavar import _METAVARS
    from .value_parser import _PARSERS

    if parser:
        _PARSERS[type_] = parser
    if metavar:
        _METAVARS[type_] = metavar
