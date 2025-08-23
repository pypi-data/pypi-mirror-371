from importlib import import_module
from types import ModuleType
from typing import Annotated

from macrotype.meta_types import emit_as, set_module
from macrotype.modules import emit_module, from_module


def test_emit_annotations_enums() -> None:
    ann = import_module("tests.annotations_new")
    mi = from_module(ann)
    lines = emit_module(mi)

    assert "from enum import Enum, IntEnum, IntFlag" in lines

    idx = lines.index("class Color(Enum):")
    assert lines[idx + 1] == "    RED = 1"
    assert lines[idx + 2] == "    GREEN = 2"

    idx = lines.index("class Priority(IntEnum):")
    assert lines[idx + 1] == "    LOW = 1"
    assert lines[idx + 2] == "    MEDIUM = 2"
    assert lines[idx + 3] == "    HIGH = 3"

    idx = lines.index("class Permission(IntFlag):")
    assert lines[idx + 1] == "    READ = 1"
    assert lines[idx + 2] == "    WRITE = 2"
    assert lines[idx + 3] == "    EXECUTE = 4"

    idx = lines.index("class StrEnum(str, Enum):")
    assert lines[idx + 1] == "    A = 'a'"
    assert lines[idx + 2] == "    B = 'b'"

    idx = lines.index("class PointEnum(Enum):")
    assert lines[idx + 1] == "    INLINE = Point"
    assert lines[idx + 2] == "    REF = Point"


def test_emit_annotations_typevars() -> None:
    ann = import_module("tests.annotations_new")
    mi = from_module(ann)
    lines = emit_module(mi)

    assert 'U = TypeVar("U", bound=str)' in lines
    assert 'NumberLike = TypeVar("NumberLike", int, float)' in lines


def test_emit_annotations_inline_meta() -> None:
    mod = ModuleType("m")
    mod.__file__ = __file__

    @emit_as("InlineMeta")
    class Inner:
        pass

    set_module(Inner, "tests.factory")

    mod.InlineMeta = Inner
    mod.__annotations__ = {"x": Annotated[int, Inner]}
    mod.x = 1

    mi = from_module(mod)
    lines = emit_module(mi)
    assert "x: Annotated[int, InlineMeta]" in lines


def test_imported_assignment_not_unpacked() -> None:
    ann = import_module("tests.annotations_new")
    mi = from_module(ann)
    lines = emit_module(mi)
    assert "from tests.modules.namespace_assign import namespace" in lines
    assert "namespace = Namespace.make" not in lines


def test_generic_overload_preserves_params() -> None:
    ann = import_module("tests.annotations_new")
    mi = from_module(ann)
    lines = emit_module(mi)

    line = next(text for text in lines if text.startswith("def first[T1, T2, *Ts]"))
    assert "TypedReturnsRows[tuple[T1, T2, Unpack[Ts]]]" in line

    line = next(text for text in lines if text.startswith("def one[T1, T2, *Ts]"))
    assert "TypedReturnsRows[tuple[T1, T2, Unpack[Ts]]]" in line


def test_sqlalchemy_generics_in_parameters_preserved() -> None:
    ann = import_module("tests.annotations_new")
    mi = from_module(ann)
    lines = emit_module(mi)

    line = next(text for text in lines if text.startswith("def count["))
    assert "SASelect[tuple[T]]" in line

    line = next(text for text in lines if text.startswith("def scalar["))
    assert "SATypedReturnsRows[tuple[T]]" in line
