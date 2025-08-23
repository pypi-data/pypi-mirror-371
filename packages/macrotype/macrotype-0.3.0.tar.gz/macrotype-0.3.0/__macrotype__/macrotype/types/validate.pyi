# Generated via: macrotype macrotype
# Do not edit by hand
from __future__ import annotations

from typing import Literal, NewType

from macrotype.types.ir import NormalizedTy, Ty, TyApp, TyRoot

annotations = annotations

NormalizedTy = NewType("NormalizedTy", TyRoot)

class TypeValidationError(TypeError): ...

Context = typing.Literal["top", "tuple_items", "call_params", "concat_args", "other"]

def validate(
    t: NormalizedTy, ctx: Literal["top", "tuple_items", "call_params", "concat_args", "other"]
) -> TyRoot: ...
def _v(
    node: Ty, ctx: Literal["top", "tuple_items", "call_params", "concat_args", "other"]
) -> None: ...
def _validate_literal_value(v: object) -> None: ...
def _validate_concatenate(node: TyApp) -> None: ...
