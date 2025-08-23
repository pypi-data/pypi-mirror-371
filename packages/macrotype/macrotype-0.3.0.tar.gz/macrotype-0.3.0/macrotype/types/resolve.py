from __future__ import annotations

from dataclasses import dataclass, replace

from .ir import (
    ParsedTy,
    ResolvedTy,
    Ty,
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

# --------- environment ---------


@dataclass(frozen=True)
class ResolveEnv:
    """
    Context for name resolution.

    imports: mapping from simple name -> actual type object
      e.g., {"User": myapp.models.User, "Box": myapp.types.Box}
    module: the current module we're resolving within (used only for provenance/error messages for now)
    """

    module: str
    imports: dict[str, type]
    # You can add: globals: dict[str, object] if you decide to eval forward refs later


# --------- implementation ---------


def resolve(t: ParsedTy | Ty, env: ResolveEnv) -> ResolvedTy:
    """Resolve forward refs and qualify bare names. Pure; returns a new tree."""
    top = t if isinstance(t, TyRoot) else TyRoot(ty=t)
    inner = _res(top.ty, env) if top.ty is not None else None
    return ResolvedTy(
        TyRoot(
            ty=inner,
            annotations=top.annotations,
            is_final=top.is_final,
            is_required=top.is_required,
            is_classvar=top.is_classvar,
        )
    )


def _res(node: Ty | None, env: ResolveEnv) -> Ty | None:
    if node is None:
        return None
    ann = node.annotations
    match node:
        case TyAny() | TyNever() | TyParamSpec() | TyTypeVar() | TyTypeVarTuple() | TyType():
            res = node

        case TyForward(qualname=qn):
            if tp := env.imports.get(qn):
                res = TyType(type_=tp)
            else:
                res = node  # leave unresolved

        case TyApp(base=base, args=args):
            base_r = _res(base, env)
            args_r = tuple(_res(a, env) for a in args)
            res = TyApp(base=base_r, args=args_r)

        case TyUnion(options=opts):
            res = TyUnion(options=tuple(_res(a, env) for a in opts))

        case TyLiteral():
            res = node

        case TyCallable(params=Ellipsis, ret=ret):
            res = TyCallable(params=Ellipsis, ret=_res(ret, env))

        case TyCallable(params=params, ret=ret):
            res = TyCallable(
                params=tuple(_res(a, env) for a in params),
                ret=_res(ret, env),
            )

        case TyUnpack(inner=inner):
            res = TyUnpack(inner=_res(inner, env))

        case _:
            res = node
    if ann:
        res = replace(res, annotations=ann)
    return res
