from __future__ import annotations

import sys
import typing as t
from collections import defaultdict
from collections.abc import Callable as ABC_Callable
from typing import Callable, Iterable

from ..emit import (
    build_name_map,
    collect_all_annotations,
    flatten_annotation_atoms,
)
from ..ir import ClassDecl, Decl, ImportBlock, ModuleDecl, TypeDefDecl

_MODULE_ALIASES: dict[str, str] = {
    "pathlib._local": "pathlib",
    "pathlib._pathlib": "pathlib",
}


def resolve_imports(mi: ModuleDecl) -> None:
    annotations = collect_all_annotations(mi)
    atoms: dict[int, t.Any] = {}
    for ann in annotations:
        atoms.update(flatten_annotation_atoms(ann))
    for sym in mi.get_all_decls():
        for deco in getattr(sym, "decorators", ()):  # capture decorator objects
            base = deco.split("(")[0].split(".")[-1]
            obj = getattr(mi.obj, base, None)
            if obj is not None:
                atoms[id(obj)] = obj

    context = mi.obj.__dict__
    name_map = build_name_map(atoms.values(), context)

    typing_names = {
        name_map[id(a)]
        for a in atoms.values()
        if (
            (
                getattr(a, "__module__", None) == "typing"
                and not isinstance(a, (t.TypeVar, t.ParamSpec, t.TypeVarTuple, t.ForwardRef))
                and a is not t.Union
            )
            or a is Callable
            or a is ABC_Callable
        )
    }
    for a in atoms.values():
        if isinstance(a, t.ForwardRef):
            name = name_map[id(a)]
            if name not in context:
                typing_names.add(name)
    typing_names.update(_collect_typing_names(mi.members))

    external: dict[str, set[str]] = defaultdict(set)
    for atom in atoms.values():
        modname = getattr(atom, "__module__", None)
        name = name_map.get(id(atom))
        if not modname or not name:
            continue
        if name in typing_names:
            continue
        modname = _MODULE_ALIASES.get(modname, modname)
        if modname in {"builtins", "typing", getattr(mi.obj, "__name__", repr(mi.obj))}:
            continue
        if modname == "enum" and name in {"Flag", "ReprEnum"}:
            continue
        if modname == "types" and name == "UnionType":
            continue
        base_name = name.split(".", 1)[0]
        external[modname].add(base_name)

    defined = {sym.name for sym in mi.members}
    for name, obj in mi.obj.__dict__.items():
        if name in defined or name.startswith("_"):
            continue
        modname = getattr(obj, "__module__", None)
        if not modname or modname in {mi.obj.__name__, "typing", "builtins"}:
            continue
        modname = _MODULE_ALIASES.get(modname, modname)
        orig_mod = sys.modules.get(modname)
        if orig_mod is None or getattr(orig_mod, name, None) is obj:
            external[modname].add(name)

    for names in external.values():
        typing_names.difference_update(names)

    existing = mi.imports
    typing_names.update(existing.typing)
    for mod, names in existing.froms.items():
        external[mod].update(names)
    mi.imports = ImportBlock(typing=typing_names, froms=dict(external))


def _collect_typing_names(symbols: Iterable[Decl]) -> set[str]:
    names: set[str] = set()
    for sym in symbols:
        if not sym.emit:
            continue
        for deco in getattr(sym, "decorators", ()):  # collect decorator names from typing
            base = deco.split("(")[0].split(".")[-1]
            if base in {"final", "override", "overload", "runtime_checkable"}:
                names.add(base)
        match sym:
            case TypeDefDecl(obj_type=alias):
                if isinstance(alias, (t.TypeVar, t.ParamSpec, t.TypeVarTuple)):
                    names.add(type(alias).__name__)
                elif alias is t.NewType:
                    names.add(getattr(alias, "__name__", repr(alias)))
            case ClassDecl(members=members):
                names.update(_collect_typing_names(members))
    return names
