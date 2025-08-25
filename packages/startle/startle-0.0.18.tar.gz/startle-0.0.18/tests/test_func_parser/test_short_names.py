from startle.inspect import make_args_from_func


def fun1(name: str = "john", /, *, count: int = 1) -> None: ...


def fun2(name: str = "john", /, *, count: int = 1, c: int = 2) -> None: ...


def fun3(name: str = "john", /, *, count: int = 1, c: int = 2) -> None:
    """
    A function.

    Args:
        name: The name of the person.
        count: The number of times to greet.
        c: The number of times to groot.
    """
    ...


def fun4(name: str = "john", /, *, count: int = 1, c: int = 2) -> None:
    """
    A function.

    Args:
        name: The name of the person.
        count [k]: The number of times to greet.
        c: The number of times to groot.
    """
    ...


def fun5(cake: str = "john", /, *, count: int = 1) -> None: ...


def fun6(cake: str = "john", /, *, count: int = 1, c: int = 2) -> None: ...


def fun7(
    cake: str = "john", /, *, count: int = 1, c: int = 2, frosting: int = 3
) -> None:
    """
    A function.

    Args:
        cake: The name of the cake.
        count: The number of times to greet.
        c: The number of times to groot.
        frosting [c]: The amount of frosting on the cake.
    """
    # Here `c` should win the short version over others
    ...


def fun8(cake: str = "john", /, *, count: int = 1, frosting: int = 3) -> None:
    """
    A function.

    Args:
        cake: The name of the cake.
        count: The number of times to greet.
        frosting [c]: The amount of frosting on the cake.
    """
    # Here `frosting` should win the short version over `count`
    ...


def fun9(
    cake: str = "john", /, *, count: int = 1, frosting: int = 3, glazing: int = 3
) -> None:
    """
    A function.

    Args:
        cake: The name of the cake.
        count: The number of times to greet.
        frosting [c]: The amount of frosting on the cake.
        glazing [c]: The amount of glazing on the cake.
    """
    # Here `frosting` should win the short version over `count`, and `glazing`
    ...


def test_short_names():
    args = make_args_from_func(fun1)
    assert args._name2idx["c"] == args._name2idx["count"]

    args = make_args_from_func(fun2)
    assert args._name2idx["c"] != args._name2idx["count"]

    args = make_args_from_func(fun3)
    assert args._name2idx["c"] != args._name2idx["count"]

    args = make_args_from_func(fun4)
    assert args._name2idx["k"] == args._name2idx["count"]
    assert args._name2idx["c"] != args._name2idx["count"]

    args = make_args_from_func(fun5)
    assert args._name2idx["c"] == args._name2idx["count"]
    assert "cake" not in args._name2idx

    args = make_args_from_func(fun6)
    assert args._name2idx["c"] != args._name2idx["count"]
    assert "cake" not in args._name2idx

    args = make_args_from_func(fun7)
    assert args._name2idx["c"] != args._name2idx["count"]
    assert args._name2idx["c"] != args._name2idx["frosting"]
    assert "cake" not in args._name2idx

    args = make_args_from_func(fun8)
    assert args._name2idx["c"] == args._name2idx["frosting"]
    assert args._name2idx["c"] != args._name2idx["count"]
    assert "cake" not in args._name2idx

    args = make_args_from_func(fun9)
    assert args._name2idx["c"] == args._name2idx["frosting"]
    assert args._name2idx["c"] != args._name2idx["count"]
    assert args._name2idx["c"] != args._name2idx["glazing"]
    assert "cake" not in args._name2idx
