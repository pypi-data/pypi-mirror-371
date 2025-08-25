from typing import Callable

from pytest import mark, raises

from startle.error import ParserConfigError, ParserOptionError

from ._utils import (
    check,
    check_exits,
    remove_trailing_spaces,
    run_w_explicit_args,
    run_w_sys_argv,
)


def hi1(name: str, count: int = 1) -> None:
    for _ in range(count):
        print(f"Hello, {name}!")


def hi2(name: str, count: int = 1, /) -> None:
    for _ in range(count):
        print(f"Hello, {name}!")


def hi3(name: str, /, count: int = 1) -> None:
    for _ in range(count):
        print(f"Hello, {name}!")


def hi4(name: str, /, *, count: int = 1) -> None:
    for _ in range(count):
        print(f"Hello, {name}!")


def hi5(name: str, *, count: int = 1) -> None:
    for _ in range(count):
        print(f"Hello, {name}!")


def hi6(*, name: str, count: int = 1) -> None:
    for _ in range(count):
        print(f"Hello, {name}!")


@mark.parametrize("hi", [hi1, hi2, hi3, hi4, hi5, hi6])
@mark.parametrize("run", [run_w_explicit_args, run_w_sys_argv])
def test_hi(capsys, run: Callable, hi: Callable) -> None:
    if hi in [hi1, hi2, hi3, hi4]:
        check(capsys, run, hi, ["Alice"], "Hello, Alice!\n")

    if hi in [hi1, hi2, hi3]:
        check(capsys, run, hi, ["Bob", "3"], "Hello, Bob!\nHello, Bob!\nHello, Bob!\n")

    if hi in [hi1, hi5, hi6]:
        check(
            capsys,
            run,
            hi,
            ["--name", "Bob", "--count", "3"],
            "Hello, Bob!\nHello, Bob!\nHello, Bob!\n",
        )
        check(
            capsys,
            run,
            hi,
            ["--count", "3", "--name", "Bob"],
            "Hello, Bob!\nHello, Bob!\nHello, Bob!\n",
        )
        check(capsys, run, hi, ["--name", "Alice"], "Hello, Alice!\n")

    if hi in [hi1, hi3, hi4, hi5]:
        check(
            capsys,
            run,
            hi,
            ["--count", "3", "Bob"],
            "Hello, Bob!\nHello, Bob!\nHello, Bob!\n",
        )
        check(
            capsys,
            run,
            hi,
            ["Bob", "--count", "3"],
            "Hello, Bob!\nHello, Bob!\nHello, Bob!\n",
        )

    if hi is hi1:
        check(
            capsys,
            run,
            hi,
            ["--name", "Bob", "3"],
            "Hello, Bob!\nHello, Bob!\nHello, Bob!\n",
        )


@mark.parametrize("hi", [hi1, hi2, hi3, hi4, hi5, hi6])
@mark.parametrize("run", [run_w_explicit_args, run_w_sys_argv])
def test_parse_err(capsys, run: Callable, hi: Callable) -> None:
    if hi in [hi1, hi5, hi6]:
        check_exits(
            capsys, run, hi, [], "Error: Required option `name` is not provided!"
        )
        check_exits(
            capsys,
            run,
            hi,
            ["--name", "Bob", "--count", "3", "--name", "Alice"],
            "Error: Option `name` is multiply given!",
        )
        check_exits(
            capsys,
            run,
            hi,
            ["--name", "Bob", "--count", "3", "--lastname", "Alice"],
            "Error: Unexpected option `lastname`!",
        )
        with raises(ParserOptionError, match="Required option `name` is not provided!"):
            run(hi, [], catch=False)
        with raises(ParserOptionError, match="Option `name` is multiply given!"):
            run(hi, ["--name", "Bob", "--count", "3", "--name", "Alice"], catch=False)
        with raises(ParserOptionError, match="Unexpected option `lastname`!"):
            run(
                hi,
                ["--name", "Bob", "--count", "3", "--lastname", "Alice"],
                catch=False,
            )
    else:
        check_exits(
            capsys,
            run,
            hi,
            [],
            "Error: Required positional argument <name> is not provided!",
        )
        with raises(
            ParserOptionError,
            match="Required positional argument <name> is not provided!",
        ):
            run(hi, [], catch=False)


@mark.parametrize("run", [run_w_explicit_args, run_w_sys_argv])
def test_config_err(capsys, run: Callable) -> None:
    def f(help: bool = False) -> None:
        pass

    def f2(dummy: str) -> None:
        pass

    check_exits(
        capsys, run, f, [], "Error: Cannot use `help` as parameter name in `f()`!"
    )
    check_exits(
        capsys, run, [f, f2], [], "Error: Cannot use `help` as parameter name in `f()`!"
    )
    with raises(
        ParserConfigError, match=r"Cannot use `help` as parameter name in `f\(\)`!"
    ):
        run(f, [], catch=False)
    with raises(
        ParserConfigError, match=r"Cannot use `help` as parameter name in `f\(\)`!"
    ):
        run([f, f2], [], catch=False)


def test_custom_program_name_help(capsys) -> None:
    def f(blip: str) -> None:
        """
        Do something.

        Args:
            blip: A string to do something with.
        """
        pass

    # here, output is not detected as a tty, so it does not use rich
    expected = """\

Do something.

Usage:
  my_program --blip <text>

where
  (pos. or opt.)  -b|--blip <text>  A string to do something with. (required)
  (option)        -?|--help         Show this help message and exit.         

"""
    with raises(SystemExit):
        run_w_sys_argv(f, ["--help"], name="my_program")
    captured = capsys.readouterr()
    assert remove_trailing_spaces(captured.out) == remove_trailing_spaces(expected)
