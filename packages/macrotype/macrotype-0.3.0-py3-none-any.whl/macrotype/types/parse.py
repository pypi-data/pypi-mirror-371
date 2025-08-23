from __future__ import annotations

import collections.abc as abc
import enum
import types as _types
import typing as t
from dataclasses import dataclass, replace
from types import EllipsisType
from typing import Optional, get_args, get_origin

from .ir import (
    LitVal,
    ParsedTy,
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

_TYPING_ATTR_TYPES: tuple[type, ...] = (type, _types.GenericAlias, str)
if hasattr(_types, "UnionType"):
    _TYPING_ATTR_TYPES += (_types.UnionType,)
TypeAliasType = getattr(t, "TypeAliasType", None)
if TypeAliasType is not None:
    _TYPING_ATTR_TYPES += (TypeAliasType,)

# ---------- Environment (minimal) ----------


@dataclass(frozen=True)
class ParseEnv:
    """Scope info used during parsing. Extend as needed."""

    module: Optional[str] = None
    typevars: dict[str, TyTypeVar] = None  # name -> TyTypeVar
    in_typed_dict: bool = False  # lets callers capture Required/NotRequired

    def get_tv(self, name: str) -> Optional[TyTypeVar]:
        if not self.typevars:
            return None
        return self.typevars.get(name)


# ---------- Helpers ----------


def _tytype_of(obj: object) -> Ty:
    # ForwardRef-like strings (e.g., "User")
    if isinstance(obj, str):
        return TyForward(qualname=obj)

    # typing.ForwardRef instance (attribute name differs across versions)
    if obj.__class__.__name__ == "ForwardRef":  # no direct import dep
        q = getattr(obj, "__forward_arg__", None) or getattr(obj, "arg", None) or str(obj)
        return TyForward(qualname=q)

    # Any / Never / bare Final
    if obj is t.Any:
        return TyAny()
    if obj is t.Never:
        return TyNever()

    # None value / NoneType
    if obj is None or obj is type(None):  # noqa: E721
        return TyType(type_=type(None))

    # Ellipsis literal
    if obj is Ellipsis:
        return TyType(type_=EllipsisType)

    # TypeVar / ParamSpec / TypeVarTuple at use-site
    if isinstance(obj, t.TypeVar):
        return TyTypeVar(
            name=obj.__name__,
            bound=_maybe_to_ir(getattr(obj, "__bound__", None)),
            constraints=tuple(_maybe_to_ir(c) for c in getattr(obj, "__constraints__", ()) or ()),
            cov=getattr(obj, "__covariant__", False),
            contrav=getattr(obj, "__contravariant__", False),
        )

    if hasattr(obj, "__class__") and obj.__class__ is t.ParamSpec:
        return TyParamSpec(name=obj.__name__)  # type: ignore[attr-defined]

    if hasattr(obj, "__class__") and obj.__class__ is t.TypeVarTuple:
        return TyTypeVarTuple(name=obj.__name__)  # type: ignore[attr-defined]

    # Classes / aliases → TyType(obj)
    return TyType(type_=obj)


def _maybe_to_ir(tp: object | None, env: Optional[ParseEnv] = None) -> Ty | None:
    return None if tp is None else _to_ir(tp, env or ParseEnv())


def _litval_of(val: object) -> LitVal:
    # Accept PEP 586 primitives / Enum / nested tuples; otherwise pass-through (repr-safe)
    if isinstance(val, (int, bool, str, bytes)) or val is None or isinstance(val, enum.Enum):
        return val  # type: ignore[return-value]
    if isinstance(val, tuple):
        return tuple(_litval_of(x) for x in val)  # type: ignore[return-value]
    # Non-strict: keep as-is (you can tighten later)
    return val  # type: ignore[return-value]


def _origin_args(tp: object) -> tuple[object | None, tuple[object, ...]]:
    origin = get_origin(tp)
    if origin is not None:
        return origin, get_args(tp)
    if not isinstance(tp, type):
        try:
            type_attr = object.__getattribute__(tp, "type")
        except AttributeError:
            pass
        else:
            if isinstance(type_attr, _TYPING_ATTR_TYPES) or get_origin(type_attr) is not None:
                return type(tp), (type_attr,)
    return None, ()


# ---------- Main parser ----------

_CACHE = {}


def _cached[T](f: T) -> T:
    def wrapped(tp: object, env: ParseEnv) -> Ty:
        origin = get_origin(tp)
        if origin in (t.ClassVar, t.Final, t.Required, t.NotRequired):
            return f(tp, env)
        cache_key = id(tp), env
        if cache_key not in _CACHE:
            _CACHE[cache_key] = f(tp, env)
        return _CACHE[cache_key]

    wrapped.wrapped = f

    return wrapped


@_cached
def _to_ir(tp: object, env: ParseEnv) -> Ty:
    """Parse a Python typing object into IR. Non-strict; preserves opaque bits."""

    origin, args = _origin_args(tp)
    if origin is None:
        if tp in (t.ClassVar, t.Final, t.Required, t.NotRequired):
            raise ValueError("Qualifiers like ClassVar/Final are only valid at the root")
        return _tytype_of(tp)

    if tp.__class__ is t.ParamSpecArgs:
        name = getattr(origin, "__name__", repr(origin))
        return TyParamSpec(name=name, flavor="args")

    if tp.__class__ is t.ParamSpecKwargs:
        name = getattr(origin, "__name__", repr(origin))
        return TyParamSpec(name=name, flavor="kwargs")

    if origin in (t.ClassVar, t.Final, t.Required, t.NotRequired):
        raise ValueError("Qualifiers like ClassVar/Final are only valid at the root")

    if origin in (t.Union, _types.UnionType):
        opts: list[Ty] = []
        for a in args:
            opts.append(_to_ir(a, env))
        uniq: dict[str, Ty] = {repr(o): o for o in opts}
        return TyUnion(options=tuple(sorted(uniq.values(), key=repr)))

    if origin is t.Annotated:
        base, *meta = args
        inner = _to_ir(base, env)
        ann = TyAnnoTree(annos=tuple(meta), child=None)
        return replace(inner, annotations=_append_ann_child(inner.annotations, ann))

    if origin is t.Literal:
        return TyLiteral(values=tuple(_litval_of(a) for a in args))

    if origin is tuple:
        if args == ((),):
            return TyApp(base=TyType(type_=tuple), args=())
        return TyApp(
            base=TyType(type_=tuple),
            args=tuple(_to_ir(a, env) for a in args),
        )

    if origin in (t.Callable, abc.Callable):
        if args and args[0] is Ellipsis:
            return TyCallable(params=Ellipsis, ret=_to_ir(args[1], env))
        if args and isinstance(args[0], (list, tuple)):
            params = tuple(_to_ir(a, env) for a in args[0])
            ret = _to_ir(args[1], env)
            return TyCallable(params=params, ret=ret)
        if args:
            return TyCallable(params=(_to_ir(args[0], env),), ret=_to_ir(args[1], env))
        return TyCallable(params=Ellipsis, ret=TyAny())

    if origin is t.Unpack:
        (inner,) = args
        return TyUnpack(inner=_to_ir(inner, env))

    if getattr(t, "Concatenate", None) is origin:
        return TyApp(
            base=TyType(type_=t.Concatenate),
            args=tuple(_to_ir(a, env) for a in args),
        )

    if origin is type:
        return TyApp(
            base=TyType(type_=type),
            args=tuple(_to_ir(a, env) for a in args),
        )

    if getattr(tp, "__module__", None) == "typing":
        base = _tytype_of(tp)
    else:
        base = _to_ir(origin, env)
    return TyApp(base=base, args=tuple(_to_ir(a, env) for a in args))


def _push_ann(tree: TyAnnoTree | None, ann: object) -> tuple[TyAnnoTree | None, object]:
    """Peel successive Annotated wrappers into a tree."""
    while get_origin(ann) is t.Annotated:
        base, *meta = get_args(ann)
        tree = TyAnnoTree(annos=tuple(meta), child=tree)
        ann = base
    return tree, ann


def _append_ann_child(tree: TyAnnoTree | None, child: TyAnnoTree | None) -> TyAnnoTree | None:
    """Append one annotation tree to another."""
    if tree is None:
        return child
    if child is None:
        return tree
    return replace(tree, child=_append_ann_child(tree.child, child))


_missing = object()


def parse_root(tp: object, env: Optional[ParseEnv] = None) -> TyRoot:
    env = env or ParseEnv()
    ann_tree: TyAnnoTree | None = None
    obj = tp
    qualifiers: set[object] = set()
    valid_qualifiers = {t.Final, t.ClassVar, t.Required, t.NotRequired}
    while True:
        ann_tree, obj = _push_ann(ann_tree, obj)
        origin = get_origin(obj)
        if origin in valid_qualifiers:
            args = get_args(obj)
            obj = args[0] if args else _missing
            qualifiers.add(origin)
        elif any(obj is q for q in valid_qualifiers):
            qualifiers.add(obj)
            obj = _missing
        else:
            break

    ty = _to_ir(obj, env) if obj is not _missing else None
    return TyRoot(
        ty=ty,
        annotations=ann_tree,
        is_final=t.Final in qualifiers,
        is_required=True
        if t.Required in qualifiers
        else False
        if t.NotRequired in qualifiers
        else None,
        is_classvar=t.ClassVar in qualifiers,
    )


def parse(tp: object, env: Optional[ParseEnv] = None) -> ParsedTy:
    return ParsedTy(parse_root(tp, env))


# Notes:
#
#     Final, ClassVar, Required, NotRequired are modeled via flags on ``TyRoot``.
#
#     Unknown/future typing.Foo[...] falls back to ``TyApp(TyType(type_=typing.Foo), args_ir)`` — lossless, pass-through.
#
#     Forward references handled both as strings and ``typing.ForwardRef``.
