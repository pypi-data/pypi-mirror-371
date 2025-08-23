"""Convert typing.NewType functions into alias symbols."""

import inspect
import typing as t

from macrotype.modules.ir import (
    ClassDecl,
    Decl,
    FuncDecl,
    ModuleDecl,
    Site,
    TypeDefDecl,
    VarDecl,
)


def _transform_decls(decls: list[Decl]) -> list[Decl]:
    new_decls: list[Decl] = []
    for decl in decls:
        match decl:
            case FuncDecl(name=name, obj=obj, comment=comment, emit=emit):
                if (
                    inspect.getattr_static(obj, "__call__", None) is not None
                    and (supertype := inspect.getattr_static(obj, "__supertype__", None))
                    is not None
                ):
                    alias = TypeDefDecl(
                        name=name,
                        value=Site(role="alias_value", annotation=supertype),
                        obj_type=t.NewType,
                        comment=comment,
                        emit=emit,
                        obj=obj,
                    )
                    new_decls.append(alias)
                else:
                    new_decls.append(decl)
            case VarDecl(name=name, obj=obj, comment=comment, emit=emit):
                if (
                    inspect.getattr_static(obj, "__call__", None) is not None
                    and (supertype := inspect.getattr_static(obj, "__supertype__", None))
                    is not None
                ):
                    alias = TypeDefDecl(
                        name=name,
                        value=Site(role="alias_value", annotation=supertype),
                        obj_type=t.NewType,
                        comment=comment,
                        emit=emit,
                        obj=obj,
                    )
                    new_decls.append(alias)
                else:
                    new_decls.append(decl)
            case ClassDecl(obj=cls, members=members):
                if isinstance(cls, type):
                    decl.members = tuple(_transform_decls(list(members)))
                new_decls.append(decl)
            case _:
                new_decls.append(decl)
    return new_decls


def transform_newtypes(mi: ModuleDecl) -> None:
    """Replace typing.NewType callables in ``mi`` with alias symbols."""

    mi.members = _transform_decls(mi.members)
