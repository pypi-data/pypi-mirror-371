from __future__ import annotations

import builtins
import enum
import typing as t
from dataclasses import InitVar
from types import EllipsisType

import pytest

from macrotype.types.ir import (
    Ty,
    TyAnnoTree,
    TyAny,
    TyApp,
    TyCallable,
    TyForward,
    TyLiteral,
    TyNever,
    TyParamSpec,
    TyRoot,
    TyType,
    TyTypeVar,
    TyTypeVarTuple,
    TyUnion,
    TyUnpack,
)
from macrotype.types.parse import _append_ann_child, parse


# ----- helpers -----
def b(name: str) -> TyType:
    if name == "Ellipsis":
        return TyType(type_=EllipsisType)
    if name == "None":
        return TyType(type_=type(None))
    return TyType(type_=getattr(builtins, name))


def typ(name: str) -> TyType:
    return TyType(type_=getattr(t, name))


# Wrap expected types in TyRoot with qualifier flags
def r(
    ty: Ty | None,
    *,
    final: bool = False,
    required: bool | None = None,
    classvar: bool = False,
    annotations: TyAnnoTree | None = None,
) -> TyRoot:
    return TyRoot(
        ty=ty, is_final=final, is_required=required, is_classvar=classvar, annotations=annotations
    )


# ----- fixtures used in tests -----
class Color(enum.Enum):
    RED = 1
    BLUE = 2


T = t.TypeVar("T")
P = t.ParamSpec("P")
Ts = t.TypeVarTuple("Ts")


# user generic
class Box(t.Generic[T]):  # noqa: D401
    """A simple generic for tests."""

    pass


# PEP 695 alias if available (Python 3.12+)
AliasListT = None
if hasattr(t, "TypeAliasType"):
    AliasListT = t.TypeAliasType("AliasListT", list[T], type_params=(T,))  # type: ignore[name-defined]


# ----- table-driven positive cases -----
CASES: list[tuple[object, TyRoot]] = [
    # atoms / basics
    (int, r(b("int"))),
    (str, r(b("str"))),
    (None, r(b("None"))),
    (t.Any, r(TyAny())),
    (t.NoReturn, r(typ("NoReturn"))),
    (t.Never, r(TyNever())),
    (t.LiteralString, r(typ("LiteralString"))),
    # Literal (PEP 586 shapes)
    (t.Literal[1, "x", True, None], r(TyLiteral(values=(1, "x", True, None)))),
    (t.Literal[Color.RED], r(TyLiteral(values=(Color.RED,)))),
    # builtins and common generics
    (dict, r(b("dict"))),
    (list, r(b("list"))),
    (tuple, r(b("tuple"))),
    (set, r(b("set"))),
    (frozenset, r(b("frozenset"))),
    (dict[int], r(TyApp(base=b("dict"), args=(b("int"),)))),
    (dict[int, str], r(TyApp(base=b("dict"), args=(b("int"), b("str"))))),
    (dict[int, t.Any], r(TyApp(base=b("dict"), args=(b("int"), TyAny())))),
    (list[int], r(TyApp(base=b("list"), args=(b("int"),)))),
    (
        list[list[int]],
        r(TyApp(base=b("list"), args=(TyApp(base=b("list"), args=(b("int"),)),))),
    ),
    (
        dict[str, list[int]],
        r(
            TyApp(
                base=b("dict"),
                args=(b("str"), TyApp(base=b("list"), args=(b("int"),))),
            )
        ),
    ),
    # tuples
    (tuple[()], r(TyApp(base=b("tuple"), args=()))),
    (tuple[int], r(TyApp(base=b("tuple"), args=(b("int"),)))),
    (tuple[int, str], r(TyApp(base=b("tuple"), args=(b("int"), b("str"))))),
    # variadic as application with Ellipsis marker
    (tuple[int, ...], r(TyApp(base=b("tuple"), args=(b("int"), b("Ellipsis"))))),
    (
        tuple[int, str, ...],
        r(TyApp(base=b("tuple"), args=(b("int"), b("str"), b("Ellipsis")))),
    ),
    # Unpack in tuples
    (t.Unpack[Ts], r(TyUnpack(inner=TyTypeVarTuple(name="Ts")))),
    (
        tuple[t.Unpack[Ts]],
        r(
            TyApp(
                base=b("tuple"),
                args=(TyUnpack(inner=TyTypeVarTuple(name="Ts")),),
            )
        ),
    ),
    (
        tuple[int, t.Unpack[Ts]],
        r(
            TyApp(
                base=b("tuple"),
                args=(b("int"), TyUnpack(inner=TyTypeVarTuple(name="Ts"))),
            )
        ),
    ),
    (
        tuple[t.Unpack[Ts], int],
        r(
            TyApp(
                base=b("tuple"),
                args=(TyUnpack(inner=TyTypeVarTuple(name="Ts")), b("int")),
            )
        ),
    ),
    # sets
    (set[int], r(TyApp(base=b("set"), args=(b("int"),)))),
    (frozenset[str], r(TyApp(base=b("frozenset"), args=(b("str"),)))),
    # dataclasses.InitVar
    (InitVar[int], r(TyApp(base=TyType(type_=InitVar), args=(b("int"),)))),
    (
        InitVar[list[int]],
        r(TyApp(base=TyType(type_=InitVar), args=(TyApp(base=b("list"), args=(b("int"),)),))),
    ),
    # unions / optionals
    (t.Union[int, str], r(TyUnion(options=(b("int"), b("str"))))),
    (int | str, r(TyUnion(options=(b("int"), b("str"))))),
    (t.Union[int, str, None], r(TyUnion(options=(b("None"), b("int"), b("str"))))),
    (
        dict[str, t.Union[int, None]],
        r(TyApp(base=b("dict"), args=(b("str"), TyUnion(options=(b("None"), b("int")))))),
    ),
    # callables
    (
        t.Callable[[int, str], bool],
        r(TyCallable(params=(b("int"), b("str")), ret=b("bool"))),
    ),
    (t.Callable[..., int], r(TyCallable(params=..., ret=b("int")))),
    (
        t.Callable[P, int],
        r(TyCallable(params=(TyParamSpec(name="P"),), ret=b("int"))),
    ),
    (
        t.Concatenate[int, P],
        r(TyApp(base=typ("Concatenate"), args=(b("int"), TyParamSpec(name="P")))),
    ),
    (
        t.Callable[t.Concatenate[int, P], int],
        r(
            TyCallable(
                params=(
                    TyApp(
                        base=typ("Concatenate"),
                        args=(b("int"), TyParamSpec(name="P")),
                    ),
                ),
                ret=b("int"),
            )
        ),
    ),
    (
        t.Callable[[t.Unpack[Ts]], int],
        r(
            TyCallable(
                params=(TyUnpack(inner=TyTypeVarTuple(name="Ts")),),
                ret=b("int"),
            )
        ),
    ),
    # Annotated
    (
        t.Annotated[int, "x"],
        r(TyType(type_=int), annotations=TyAnnoTree(annos=("x",))),
    ),
    # ClassVar / Final / Required / NotRequired
    (t.ClassVar[int], r(b("int"), classvar=True)),
    (t.Final[int], r(b("int"), final=True)),
    (t.Final, r(None, final=True)),
    (t.NotRequired[int], r(b("int"), required=False)),
    (t.Required[str], r(b("str"), required=True)),
    # variables / binders (declaration-like leaves appearing at use sites)
    (
        T,
        r(TyTypeVar(name="T", bound=None, constraints=(), cov=False, contrav=False)),
    ),
    (P, r(TyParamSpec(name="P"))),
    (P.args, r(TyParamSpec(name="P", flavor="args"))),
    (P.kwargs, r(TyParamSpec(name="P", flavor="kwargs"))),
    (t.Unpack[P.args], r(TyUnpack(inner=TyParamSpec(name="P", flavor="args")))),
    (t.Unpack[P.kwargs], r(TyUnpack(inner=TyParamSpec(name="P", flavor="kwargs")))),
    (Ts, r(TyTypeVarTuple(name="Ts"))),
    (t.Unpack[Ts], r(TyUnpack(inner=TyTypeVarTuple(name="Ts")))),
    # typing.Type / builtins.type
    (t.Type[int], r(TyApp(base=b("type"), args=(b("int"),)))),
    # forward ref by string
    ("User", r(TyForward(qualname="User"))),
    # collections.abc generics parse (kept as names/apps; normalization can fold later)
    (t.Deque[int], r(TyApp(base=TyType(type_=t.Deque[int]), args=(b("int"),)))),
]

# Optional cases depending on runtime features
if AliasListT is not None:
    CASES.append(
        (
            AliasListT[int],
            r(TyApp(base=TyType(type_=AliasListT), args=(b("int"),))),
        )
    )


def test_parse_table_driven():
    assert CASES == [(src, parse(src)) for src, _ in CASES]


def test_user_generic_application():
    got = parse(Box[int]).ty
    assert isinstance(got, TyApp)
    assert isinstance(got.base, TyType)
    assert got.base.type_ is Box
    assert got.args == (b("int"),)


def test_append_ann_child():
    inner = TyAnnoTree(annos=("a",))
    outer = TyAnnoTree(annos=("b",))
    merged = _append_ann_child(inner, outer)
    assert merged.annos == ("a",)
    assert merged.child and merged.child.annos == ("b",)


def test_union_order_insensitive():
    a = parse(int | str)
    b = parse(str | int)
    assert a == b


def test_inner_final_disallowed():
    with pytest.raises(ValueError):
        parse(list[t.Final[int]])
