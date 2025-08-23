from __future__ import annotations

import inspect
import linecache
import textwrap
import types
import typing as t
from types import ModuleType

import pytest

from macrotype.meta_types import clear_registry
from macrotype.modules.ir import ClassDecl, FuncDecl, ModuleDecl, Site, TypeDefDecl, VarDecl
from macrotype.modules.scanner import scan_module
from macrotype.modules.transformers import (
    add_comments,
    apply_dataclass_transform,
    canonicalize_foreign_symbols,
    canonicalize_local_aliases,
    expand_overloads,
    infer_constant_types,
    infer_param_defaults,
    normalize_descriptors,
    normalize_flags,
    prune_inherited_typeddict_fields,
    prune_protocol_methods,
    synthesize_aliases,
    transform_dataclasses,
    transform_enums,
    transform_generics,
    transform_namedtuples,
    transform_newtypes,
    unwrap_decorated_functions,
)


def mod_from_code(code: str, name: str) -> ModuleType:
    module = ModuleType(name)
    code = textwrap.dedent(code)
    filename = "<" + name + ">"
    linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)
    module.__file__ = filename
    exec(compile(code, filename, "exec"), module.__dict__)
    return module


def test_add_comment_transform() -> None:
    code = """
    x: int = 0  # variable comment

    type Alias = int  # alias comment

    """
    mod = mod_from_code(code, "comments")
    mi = scan_module(mod)
    add_comments(mi)
    by_name = {s.name: s for s in mi.members}

    x = by_name["x"]
    assert x.comment == "variable comment"

    alias = by_name["Alias"]
    assert isinstance(alias, TypeDefDecl)
    assert alias.comment == "alias comment"
    assert alias.value.comment == "alias comment"


def test_alias_transform() -> None:
    code = """
    from typing import TypeAliasType, TypeVar, TypeAlias

    T = TypeVar("T")
    Alias = TypeAliasType("Alias", list[T], type_params=(T,))
    """
    mod = mod_from_code(code, "alias")
    mi = scan_module(mod)
    synthesize_aliases(mi)
    by_name = {s.name: s for s in mi.members}

    alias = t.cast(TypeDefDecl, by_name["Alias"])
    assert alias.type_params == ("T",)
    assert t.get_origin(alias.value.annotation) is list


def test_typevar_alias_transform() -> None:
    code = """
    from typing import TypeVar, ParamSpec, TypeVarTuple

    T = TypeVar("T")
    P = ParamSpec("P")
    Ts = TypeVarTuple("Ts")
    """
    mod = mod_from_code(code, "typevars")
    mi = scan_module(mod)
    synthesize_aliases(mi)
    by_name = {s.name: s for s in mi.members}

    t_alias = by_name["T"]
    p_alias = by_name["P"]
    ts_alias = by_name["Ts"]

    assert isinstance(t_alias, TypeDefDecl)
    assert isinstance(p_alias, TypeDefDecl)
    assert isinstance(ts_alias, TypeDefDecl)


def test_genericalias_transform() -> None:
    code = """
    Alias = list[int]
    """
    mod = mod_from_code(code, "ga")
    mi = scan_module(mod)
    synthesize_aliases(mi)
    alias = t.cast(TypeDefDecl, {s.name: s for s in mi.members}["Alias"])
    assert isinstance(alias.obj_type, types.GenericAlias)
    assert alias.value.annotation == list[int]


def test_newtype_transform() -> None:
    code = """
    from typing import NewType

    UserId = NewType("UserId", int)
    """
    mod = mod_from_code(code, "newtype")
    mi = scan_module(mod)
    transform_newtypes(mi)
    by_name = {s.name: s for s in mi.members}
    user = by_name["UserId"]
    assert isinstance(user, TypeDefDecl)
    assert user.obj_type is t.NewType
    assert user.value and user.value.annotation is int


def test_constant_transform() -> None:
    class CustomInt(int):
        pass

    members = [
        VarDecl(
            name="ANSWER", site=Site(role="var", name="ANSWER", annotation=inspect._empty), obj=42
        ),
        VarDecl(
            name="GREETING",
            site=Site(role="var", name="GREETING", annotation=inspect._empty),
            obj="hi",
        ),
        VarDecl(
            name="RATE", site=Site(role="var", name="RATE", annotation=inspect._empty), obj=1.5
        ),
        VarDecl(
            name="FLAG", site=Site(role="var", name="FLAG", annotation=inspect._empty), obj=True
        ),
        VarDecl(
            name="CUSTOM",
            site=Site(role="var", name="CUSTOM", annotation=inspect._empty),
            obj=CustomInt(1),
        ),
    ]
    mi = ModuleDecl(name="consts", obj=ModuleType("consts"), members=members)
    infer_constant_types(mi)
    by_name = {s.name: s for s in mi.members}
    ans = t.cast(VarDecl, by_name["ANSWER"])
    greet = t.cast(VarDecl, by_name["GREETING"])
    rate = t.cast(VarDecl, by_name["RATE"])
    flag = t.cast(VarDecl, by_name["FLAG"])
    custom = t.cast(VarDecl, by_name["CUSTOM"])
    assert ans.site.annotation is int
    assert greet.site.annotation is str
    assert rate.site.annotation is float
    assert flag.site.annotation is bool
    assert custom.site.annotation is inspect._empty


def test_dataclass_transform() -> None:
    code = """
    from dataclasses import dataclass

    @dataclass(order=True)
    class DC:
        x: int
        def user(self) -> None: ...

    @dataclass
    class Outer:
        y: int
        @dataclass
        class Inner:
            z: int
    """
    mod = mod_from_code(code, "dataclasses")
    mi = scan_module(mod)
    transform_dataclasses(mi)
    apply_dataclass_transform(mi)
    by_name = {s.name: s for s in mi.members}

    dc = t.cast(ClassDecl, by_name["DC"])
    assert "dataclass(order=True)" in dc.decorators
    member_names = {m.name for m in dc.members}
    assert "__init__" not in member_names
    assert "__lt__" not in member_names

    outer = t.cast(ClassDecl, by_name["Outer"])
    assert "dataclass" in outer.decorators
    inner = next(m for m in outer.members if isinstance(m, ClassDecl) and m.name == "Inner")
    assert "dataclass" in inner.decorators


def test_dataclass_transform_carrier() -> None:
    code = """
    from typing import dataclass_transform

    @dataclass_transform()
    class Base:
        def __init_subclass__(cls) -> None:
            cls.__dataclass_fields__ = {"x": object(), "y": object()}
            def __init__(self, x: int, y: int) -> None: ...
            cls.__init__ = __init__

    class Sub(Base):
        x: int
        y: int
    """
    mod = mod_from_code(code, "dc_transform")
    mi = scan_module(mod)
    transform_dataclasses(mi)
    apply_dataclass_transform(mi)
    by_name = {s.name: s for s in mi.members}

    base = t.cast(ClassDecl, by_name["Base"])
    assert any(d.startswith("dataclass_transform") for d in base.decorators)

    sub = t.cast(ClassDecl, by_name["Sub"])
    assert all(not d.startswith("dataclass") for d in sub.decorators)
    assert "__init__" not in {m.name for m in sub.members}


def test_dataclass_transform_import() -> None:
    code = """
    class Base:
        __dataclass_transform__ = {}

    class Sub(Base):
        pass
    """
    mod = mod_from_code(code, "dc_transform_import")
    mi = scan_module(mod)
    transform_dataclasses(mi)
    apply_dataclass_transform(mi)
    by_name = {s.name: s for s in mi.members}
    base = t.cast(ClassDecl, by_name["Base"])
    assert "dataclass_transform()" in base.decorators
    assert "dataclass_transform" in mi.imports.typing


def test_descriptor_transform() -> None:
    code = """
    import functools

    class D:
        @property
        def prop(self) -> int: ...
        @prop.setter
        def prop(self, v: int) -> None: ...
        @prop.deleter
        def prop(self) -> None: ...

        @classmethod
        def clsmeth(cls) -> None: ...

        @staticmethod
        def stat() -> None: ...

        @functools.cached_property
        def cache(self) -> int: ...

        def base(self, a: int, b: str) -> str: ...
        pm = functools.partialmethod(base, 2)
    """
    mod = mod_from_code(code, "descriptor")
    mi = scan_module(mod)
    normalize_descriptors(mi)
    dcls = t.cast(
        ClassDecl, next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "D")
    )
    props = [m for m in dcls.members if m.name == "prop" and isinstance(m, FuncDecl)]
    decos = {tuple(m.decorators) for m in props}
    assert ("property",) in decos
    assert ("prop.setter",) in decos
    assert ("prop.deleter",) in decos
    cm = next(m for m in dcls.members if isinstance(m, FuncDecl) and m.name == "clsmeth")
    assert cm.decorators == ("classmethod",)
    sm = next(m for m in dcls.members if isinstance(m, FuncDecl) and m.name == "stat")
    assert sm.decorators == ("staticmethod",)
    cp = next(m for m in dcls.members if isinstance(m, FuncDecl) and m.name == "cache")
    assert cp.decorators == ("cached_property",)
    pm = next(m for m in dcls.members if isinstance(m, FuncDecl) and m.name == "pm")
    assert pm.decorators == ()
    assert [p.name for p in pm.params] == ["self", "b"]
    assert pm.params[1].annotation in (str, "str")
    assert pm.ret and pm.ret.annotation in (str, "str")


def test_flag_transform() -> None:
    code = """
    from typing import final, override
    import abc

    @final
    class Base:
        def meth(self) -> None: ...

    class Derived(Base):
        @override
        def meth(self) -> None: ...

    class Abstract(abc.ABC):
        @abc.abstractmethod
        def abst(self) -> None: ...

    @final
    def f() -> None: ...
    """
    mod = mod_from_code(code, "flags")
    mi = scan_module(mod)
    normalize_flags(mi)
    by_name = {s.name: s for s in mi.members}

    base = t.cast(ClassDecl, by_name["Base"])
    assert base.flags.get("final") is True
    assert "final" in base.decorators

    derived = t.cast(ClassDecl, by_name["Derived"])
    meth = next(m for m in derived.members if isinstance(m, FuncDecl) and m.name == "meth")
    assert meth.flags.get("override") is True
    assert "override" in meth.decorators

    abstract = t.cast(ClassDecl, by_name["Abstract"])
    assert abstract.flags.get("abstract") is True
    abst = next(m for m in abstract.members if isinstance(m, FuncDecl) and m.name == "abst")
    assert abst.flags.get("abstract") is True
    assert "abstractmethod" in abst.decorators

    func = t.cast(FuncDecl, by_name["f"])
    assert func.flags.get("final") is True
    assert "final" not in func.decorators


def test_runtime_checkable_transform() -> None:
    code = """
    from typing import Protocol, runtime_checkable

    class P(Protocol):
        def run(self) -> int: ...

    P = runtime_checkable(P)
    """
    mod = mod_from_code(code, "runtime")
    mi = scan_module(mod)
    prune_protocol_methods(mi)
    cls = next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "P")
    assert "runtime_checkable" in cls.decorators


def test_foreign_symbol_transform() -> None:
    code = """

    class Dummy:
        __module__ = "other"
        __name__ = "Dummy"

    external = Dummy()
    const = 1
    annotated: int = 2

    def local() -> None: ...
    """
    mod = mod_from_code(code, "foreign")
    mi = scan_module(mod)
    canonicalize_foreign_symbols(mi)
    by_name = {s.name: s for s in mi.members}

    external = by_name["external"]
    assert isinstance(external, TypeDefDecl)
    const = by_name["const"]
    assert isinstance(const, VarDecl)
    annotated = by_name["annotated"]
    assert isinstance(annotated, VarDecl)


def test_local_alias_transform() -> None:
    code = """
    def func(x: int) -> int:
        return x

    alias = func
    """
    mod = mod_from_code(code, "local_alias")
    mi = scan_module(mod)
    canonicalize_local_aliases(mi)
    unwrap_decorated_functions(mi)
    by_name = {s.name: s for s in mi.members}

    alias = by_name["alias"]
    assert isinstance(alias, TypeDefDecl)
    funcs = [s for s in mi.members if isinstance(s, FuncDecl)]
    assert len(funcs) == 1


def test_overload_transform() -> None:
    clear_registry()
    code = """
    from macrotype.meta_types import overload, overload_for

    @overload
    def foo(x: int) -> int: ...
    @overload
    def foo(x: str) -> str: ...
    def foo(x): ...

    class C:
        @overload
        def bar(self, x: int) -> int: ...
        @overload
        def bar(self, x: str) -> str: ...
        def bar(self, x): ...

    @overload_for(1)
    @overload_for("a")
    @overload_for(b"b")
    def lit(x):
        return x
    """
    mod = mod_from_code(code, "overload")
    mi = scan_module(mod)
    expand_overloads(mi)
    by_name = [s for s in mi.members if isinstance(s, FuncDecl) and s.name == "foo"]
    assert len(by_name) == 3
    assert all("overload" in s.decorators for s in by_name[:-1])
    assert "overload" not in by_name[-1].decorators
    cls = next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "C")
    bars = [m for m in cls.members if isinstance(m, FuncDecl) and m.name == "bar"]
    assert len(bars) == 3
    assert all("overload" in m.decorators for m in bars[:-1])
    assert "overload" not in bars[-1].decorators
    lits = [s for s in mi.members if isinstance(s, FuncDecl) and s.name == "lit"]
    assert len(lits) == 4
    assert all("overload" in s.decorators for s in lits[:-1])
    assert "overload" not in lits[-1].decorators


def test_protocol_transform() -> None:
    code = """
    from typing import Protocol

    class P(Protocol):
        def meth(self) -> None: ...
    """
    mod = mod_from_code(code, "proto")
    mi = scan_module(mod)
    prune_protocol_methods(mi)
    proto = t.cast(
        ClassDecl, next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "P")
    )
    member_names = {m.name for m in proto.members if isinstance(m, FuncDecl)}
    assert member_names == {"meth"}


def test_protocol_prunes_explicit_methods() -> None:
    code = """
    from typing import Protocol

    class P(Protocol):
        def __init__(self, x: int) -> None: ...
        @classmethod
        def __subclasshook__(cls, other: type) -> bool: ...
        def meth(self) -> None: ...
    """
    mod = mod_from_code(code, "proto_explicit")
    mi = scan_module(mod)
    prune_protocol_methods(mi)
    proto = t.cast(
        ClassDecl, next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "P")
    )
    member_names = {m.name for m in proto.members if isinstance(m, FuncDecl)}
    assert member_names == {"meth"}


@pytest.mark.skip(reason="TypedDict base classes not in MRO at runtime")
def test_typeddict_transform() -> None:
    code = """
    from typing import TypedDict

    class Base(TypedDict):
        a: int
        b: str

    class Derived(Base):
        b: str
        c: float
    """
    mod = mod_from_code(code, "typeddict")
    mi = scan_module(mod)
    prune_inherited_typeddict_fields(mi)
    derived = next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "Derived")
    assert len(derived.td_fields) == 1
    assert derived.td_fields[0].name == "c"
    assert derived.td_total is None


def test_namedtuple_transform() -> None:
    code = """
    import typing as t

    class NT(t.NamedTuple):
        x: int
        y: int
    """
    mod = mod_from_code(code, "namedtuple")
    mi = scan_module(mod)
    canonicalize_foreign_symbols(mi)
    transform_namedtuples(mi)
    nt = t.cast(
        ClassDecl, next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "NT")
    )
    assert [b.annotation for b in nt.bases][0] is t.NamedTuple
    member_names = {m.name for m in nt.members}
    assert member_names == {"x", "y"}


def test_enum_transform() -> None:
    code = """
    from enum import Enum, IntFlag

    class Color(Enum):
        RED = 1
        GREEN = 2
        def describe(self) -> str: ...

    class Permission(IntFlag):
        READ = 1
        WRITE = 2
    """
    mod = mod_from_code(code, "enums")
    mi = scan_module(mod)
    transform_enums(mi)
    color = t.cast(
        ClassDecl, next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "Color")
    )
    aliases = [m for m in color.members if isinstance(m, TypeDefDecl)]
    assert [a.name for a in aliases] == ["RED", "GREEN"]
    methods = {m.name for m in color.members if isinstance(m, FuncDecl)}
    assert "describe" in methods and "__new__" not in methods
    perm = t.cast(
        ClassDecl,
        next(s for s in mi.members if isinstance(s, ClassDecl) and s.name == "Permission"),
    )
    perm_aliases = [m.name for m in perm.members if isinstance(m, TypeDefDecl)]
    assert perm_aliases == ["READ", "WRITE"]
    perm_methods = {m.name for m in perm.members if isinstance(m, FuncDecl)}
    assert "__or__" not in perm_methods


def test_unwrap_decorated_function_transform() -> None:
    code = """
    class Wrapper:
        def __init__(self, fn):
            self._fn = fn
            self.__wrapped__ = fn
        def __call__(self, *a, **kw):
            return self._fn(*a, **kw)

    def deco(fn):
        return Wrapper(fn)

    @deco
    def wrapped(x: int) -> str:
        return str(x)
    """
    mod = mod_from_code(code, "decorated")
    mi = scan_module(mod)
    unwrap_decorated_functions(mi)
    fn = next(s for s in mi.members if isinstance(s, FuncDecl) and s.name == "wrapped")
    assert [p.name for p in fn.params] == ["x"]
    assert fn.ret and fn.ret.annotation in (str, "str")


def test_infer_param_defaults_transform() -> None:
    code = """
    def mult(a, b=1):
        return a * b
    """
    mod = mod_from_code(code, "param_defaults")
    mi = scan_module(mod)
    infer_param_defaults(mi)
    fn = next(s for s in mi.members if isinstance(s, FuncDecl) and s.name == "mult")
    assert [p.name for p in fn.params] == ["a", "b"]
    assert fn.params[0].annotation is inspect._empty
    assert fn.params[1].annotation in (int, "int")


def test_generic_transform() -> None:
    code = """
    from typing import Generic, TypeVar, TypeVarTuple

    T = TypeVar("T")
    Ts = TypeVarTuple("Ts")

    class Box(Generic[T]):
        pass

    class Variadic(Generic[*Ts]):
        pass
    """
    mod = mod_from_code(code, "generic")
    mi = scan_module(mod)
    transform_generics(mi)
    by_name = {s.name: s for s in mi.members}

    box = t.cast(ClassDecl, by_name["Box"])
    assert box.type_params == ("T",)
    assert all(
        getattr(b.annotation, "__origin__", b.annotation) is not t.Generic for b in box.bases
    )

    var = t.cast(ClassDecl, by_name["Variadic"])
    assert var.type_params == ("*Ts",)


def test_function_generic_transform() -> None:
    code = """
    from typing import Callable, Concatenate, ParamSpec, TypeVar, TypeVarTuple

    T = TypeVar("T")
    Ts = TypeVarTuple("Ts")
    P = ParamSpec("P")

    def func(x: T, *args: *Ts, **kwargs: P) -> T:
        return x

    def wrap(fn: Callable[Concatenate[int, P], T]) -> Callable[P, T]:
        return fn
    """
    mod = mod_from_code(code, "fn_generic")
    mi = scan_module(mod)
    transform_generics(mi)
    fn = next(s for s in mi.members if isinstance(s, FuncDecl) and s.name == "func")
    assert fn.type_params == ("**P", "*Ts", "T")
    wrap = next(s for s in mi.members if isinstance(s, FuncDecl) and s.name == "wrap")
    assert wrap.type_params == ("**P", "T")
