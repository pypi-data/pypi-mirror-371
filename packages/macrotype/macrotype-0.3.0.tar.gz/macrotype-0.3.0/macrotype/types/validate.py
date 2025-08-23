from __future__ import annotations

import inspect
import typing as t
from types import EllipsisType
from typing import Literal

from .ir import (
    NormalizedTy,
    Ty,
    TyAny,
    TyApp,
    TyCallable,
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


class TypeValidationError(TypeError):
    pass


# Where in the tree we are, to validate context-sensitive nodes.
Context = Literal["top", "tuple_items", "call_params", "concat_args", "other"]


def validate(t: NormalizedTy, *, ctx: Context = "top") -> TyRoot:
    _v(t.ty, ctx=ctx)
    return t


def _v(node: Ty, *, ctx: Context) -> None:
    match node:
        # Leaves / benign
        case TyAny() | TyNever() | TyTypeVar() | TyParamSpec() | TyTypeVarTuple():
            return

        # Names: only special-case Ellipsis outside allowed spots
        case TyType(type_=tp):
            if tp is EllipsisType and ctx not in ("tuple_items", "concat_args"):
                raise TypeValidationError(
                    "Ellipsis is only valid in tuple[...] or Concatenate[...] contexts"
                )
            return

        # Literal values must be PEP-586 legal (we assume parser kept them legal)
        case TyLiteral(values=vals):
            for v in vals:
                _validate_literal_value(v)
            return

        # tuple[...] forms (fixed-length or variadic)
        case TyApp(base=TyType(type_=tuple), args=args):
            if any(isinstance(a, TyTypeVarTuple) for a in args):
                raise TypeValidationError(
                    "TypeVarTuple in tuple[...] must be wrapped in Unpack[...]"
                )
            # Ellipsis, if present, must be last; only one allowed
            ell_count = sum(1 for a in args if isinstance(a, TyType) and a.type_ is EllipsisType)
            if ell_count:
                if not (isinstance(args[-1], TyType) and args[-1].type_ is EllipsisType):
                    raise TypeValidationError("In tuple[...,], Ellipsis must be the final argument")
                if ell_count > 1:
                    raise TypeValidationError("Only one Ellipsis allowed in tuple[...]")
                for a in args[:-1]:
                    _v(a, ctx="tuple_items")
            else:
                # Treat as a fixed tuple spelled via TyApp — allow but validate elems
                for a in args:
                    _v(a, ctx="tuple_items")
            return

        # Generic application other than tuple[...] — validate base/args recursively
        case TyApp(base=b, args=as_):
            _v(b, ctx="other")
            for a in as_:
                _v(a, ctx="other")
            return

        # Union: non-empty, validate members
        case TyUnion(options=opts):
            if len(opts) == 0:
                raise TypeValidationError("Empty union is invalid")
            for o in opts:
                _v(o, ctx="other")
            return

        # Callable forms:
        #   Callable[..., R]
        #   Callable[[T1, ...], R]
        #   Callable[P, R]
        #   Callable[Concatenate[head..., P], R]
        case TyCallable(params=Ellipsis, ret=r):
            _v(r, ctx="other")
            return
        case TyCallable(params=ps, ret=r):
            assert ps is not Ellipsis
            # Ensure params is a tuple for uniform handling
            ps = tuple(ps)
            # Validate parameter list
            pspecs = sum(1 for p in ps if isinstance(p, TyParamSpec))
            if pspecs > 1:
                raise TypeValidationError("Only one ParamSpec allowed in Callable parameters")
            if pspecs == 1 and len(ps) != 1:
                # Only bare P is allowed, else it must be wrapped in Concatenate
                raise TypeValidationError(
                    "ParamSpec alone must be the sole parameter in Callable[P, R]"
                )
            if (
                len(ps) == 1
                and isinstance(ps[0], TyApp)
                and isinstance(ps[0].base, TyType)
                and ps[0].base.type_ is t.Concatenate
            ):
                _validate_concatenate(ps[0])
            else:
                for p in ps:
                    if isinstance(p, TyUnpack):
                        raise TypeValidationError(
                            "Unpack[...] not valid directly in Callable parameter list"
                        )
                    _v(p, ctx="call_params")
            _v(r, ctx="other")
            return

        # Unpack can only appear in tuple items or Concatenate args
        case TyUnpack(inner=i):
            if ctx in ("tuple_items", "concat_args"):
                # At the type level we only allow TypeVarTuple inside Unpack
                if not isinstance(i, TyTypeVarTuple):
                    raise TypeValidationError(
                        "Unpack must wrap a TypeVarTuple at the type level",
                    )
                return
            if ctx in {"call_params", "top"}:
                if ctx == "top" and isinstance(i, TyTypeVarTuple):
                    raise TypeValidationError("Unpack[TypeVarTuple] is not valid at the top level")
                _v(i, ctx="other")
                return
            raise TypeValidationError(
                "Unpack[...] is only valid inside tuple[...] or Concatenate[...] or as a parameter annotation"
            )

        # Fallback: accept but walk children if any were added later
        case _:
            return


def _validate_literal_value(v: object) -> None:
    # Parser should have filtered already; keep a defensive check
    if isinstance(v, (int, bool, str, bytes)) or v is None:
        return
    # Enums are ok
    if inspect.getattr_static(v, "__class__", None) and any(
        cls.__name__ == "Enum" for cls in type(v).__mro__
    ):
        return
    if isinstance(v, tuple):
        for x in v:
            _validate_literal_value(x)
        return
    raise TypeValidationError(f"Illegal Literal value: {type(v).__name__!s}")


def _validate_concatenate(node: TyApp) -> None:
    # typing.Concatenate[head..., P] — last arg must be ParamSpec; heads are regular types (no Unpack)
    assert isinstance(node.base, TyType) and node.base.type_ is t.Concatenate
    if not node.args:
        raise TypeValidationError("Concatenate[...] must have at least one argument")
    *heads, tail = node.args
    if not isinstance(tail, TyParamSpec):
        raise TypeValidationError("Last argument of Concatenate[...] must be a ParamSpec")
    for h in heads:
        if isinstance(h, TyUnpack):
            raise TypeValidationError("Unpack[...] not allowed in Concatenate head arguments")
        _v(h, ctx="concat_args")
