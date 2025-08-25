import inspect
from dataclasses import MISSING, fields, is_dataclass
from inspect import Parameter
from typing import (
    Any,
    Callable,
    Iterable,
    cast,
    get_args,
    get_origin,
)

from ._docstr import (
    _DocstrParam,
    _DocstrParams,
    _parse_class_docstring,
    _parse_func_docstring,
)
from ._type_utils import _normalize_type, _shorten_type_annotation, _strip_annotated
from .arg import Arg, Name
from .args import Args
from .error import ParserConfigError
from .value_parser import is_parsable


def _get_default_factories(cls: type) -> dict[str, Any]:
    """
    Get the default factory functions for all fields in a dataclass.
    """
    if not is_dataclass(cls):
        raise ValueError(f"{cls} is not a dataclass")

    return {
        f.name: f.default_factory
        for f in fields(cls)
        if f.default_factory is not MISSING
    }


def _make_args_from_params(
    params: Iterable[tuple[str, Parameter]],
    obj_name: str,
    brief: str = "",
    arg_helps: _DocstrParams = {},
    program_name: str = "",
    default_factories: dict[str, Any] = {},
) -> Args:
    args = Args(brief=brief, program_name=program_name)

    used_short_names = set()

    for param_name, _ in params:
        if param_name == "help":
            raise ParserConfigError(
                f"Cannot use `help` as parameter name in `{obj_name}`!"
            )

    # Discover if there are any named options that are of length 1
    # If so, those cannot be used as short names for other options
    for param_name, param in params:
        if param.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
            if len(param_name) == 1:
                used_short_names.add(param_name)

    # Discover if there are any docstring-specified short names,
    # these also take precedence over the first letter of the parameter name
    for param_name, param in params:
        if param.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
            if docstr_param := arg_helps.get(param_name):
                if docstr_param.short_name:
                    # if this name is already used, this param cannot use it
                    if docstr_param.short_name in used_short_names:
                        docstr_param.short_name = None
                    else:
                        used_short_names.add(docstr_param.short_name)

    # Iterate over the parameters and add arguments based on kind
    for param_name, param in params:
        normalized_annotation = (
            str
            if param.annotation is Parameter.empty
            else _normalize_type(_strip_annotated(param.annotation))
        )

        if param.default is not inspect.Parameter.empty:
            required = False
            default = param.default
        else:
            required = True
            default = None

        default_factory = default_factories.get(param_name, None)

        param_key: str | None = None
        if param_name in arg_helps:
            param_key = param_name
        elif param.kind is Parameter.VAR_POSITIONAL and f"*{param_name}" in arg_helps:
            # admit both "arg" and "*arg" as valid names
            param_key = f"*{param_name}"
        elif param.kind is Parameter.VAR_KEYWORD and f"**{param_name}" in arg_helps:
            # admit both "arg" and "**arg" as valid names
            param_key = f"**{param_name}"

        docstr_param = arg_helps[param_key] if param_key else _DocstrParam()

        param_name_sub = param_name.replace("_", "-")
        positional = False
        named = False
        name = Name(long=param_name_sub)
        metavar = ""
        nary = False
        container_type: type | None = None

        if param.kind in [
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.VAR_POSITIONAL,
        ]:
            positional = True
        if param.kind in [
            Parameter.KEYWORD_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.VAR_KEYWORD,
        ]:
            named = True
            if len(param_name) == 1:
                name = Name(short=param_name_sub)
            elif docstr_param.short_name:
                # no need to check used_short_names, this name is already in there
                name = Name(short=docstr_param.short_name, long=param_name_sub)
            elif param_name[0] not in used_short_names:
                name = Name(short=param_name_sub[0], long=param_name_sub)
                used_short_names.add(param_name_sub[0])
            else:
                name = Name(long=param_name_sub)

        if param.kind is Parameter.VAR_POSITIONAL:
            nary = True
            container_type = list

        # for n-ary options, type should refer to the inner type
        # if inner type is absent from the hint, assume str

        orig = get_origin(normalized_annotation)
        args_ = get_args(normalized_annotation)

        if orig in [list, set]:
            nary = True
            container_type = orig
            normalized_annotation = _strip_annotated(args_[0]) if args_ else str
        elif orig is tuple and len(args_) == 2 and args_[1] is ...:
            nary = True
            container_type = orig
            normalized_annotation = _strip_annotated(args_[0]) if args_ else str
        elif normalized_annotation in [list, tuple, set]:
            normalized_annotation = cast(type, normalized_annotation)
            nary = True
            container_type = normalized_annotation
            normalized_annotation = str

        if not is_parsable(normalized_annotation):
            raise ParserConfigError(
                f"Unsupported type `{_shorten_type_annotation(param.annotation)}` "
                f"for parameter `{param_name}` in `{obj_name}`!"
            )

        # the following should hold if normalized_annotation is parsable
        normalized_annotation = cast(type, normalized_annotation)

        arg = Arg(
            name=name,
            type_=normalized_annotation,
            container_type=container_type,
            metavar=metavar,
            help=docstr_param.desc,
            required=required,
            default=default,
            default_factory=default_factory,
            is_positional=positional,
            is_named=named,
            is_nary=nary,
        )
        if param.kind is Parameter.VAR_POSITIONAL:
            arg.name = Name()
            args.enable_unknown_args(arg)
        elif param.kind is Parameter.VAR_KEYWORD:
            arg.name = Name(long="<key>")
            args.enable_unknown_opts(arg)
        else:
            args.add(arg)

    return args


def make_args_from_func(func: Callable, program_name: str = "") -> Args:
    # Get the signature of the function
    sig = inspect.signature(func)
    params = sig.parameters.items()

    # Attempt to parse brief and arg descriptions from docstring
    brief, arg_helps = _parse_func_docstring(func)

    return _make_args_from_params(
        params, f"{func.__name__}()", brief, arg_helps, program_name
    )


def make_args_from_class(cls: type, program_name: str = "", brief: str = "") -> Args:
    # TODO: check if cls is a class?

    func = cls.__init__  # type: ignore
    # (mypy thinks cls is an instance)

    # Get the signature of the initializer
    sig = inspect.signature(func)

    # name of the first parameter (usually `self`)
    self_name = next(iter(sig.parameters))

    # filter out the first parameter
    params = [
        (name, param) for name, param in sig.parameters.items() if name != self_name
    ]

    arg_helps = _parse_class_docstring(cls)
    default_factories = _get_default_factories(cls) if is_dataclass(cls) else {}

    return _make_args_from_params(
        params, cls.__name__, brief, arg_helps, program_name, default_factories
    )
