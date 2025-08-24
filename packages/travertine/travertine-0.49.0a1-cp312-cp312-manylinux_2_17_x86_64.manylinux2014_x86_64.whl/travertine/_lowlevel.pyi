from __future__ import annotations

import typing as t
from datetime import datetime, timedelta

from xotless.types import TEq, TOrd

from .types import Result

ProcedureIndex = int

class Program:
    def __init__(self, capacity: t.Optional[int] = None) -> None: ...
    @property
    def procedure_index(self) -> ProcedureIndex: ...
    def copy(self) -> Program: ...
    def add_identity_procedure(self, index: ProcedureIndex, proc: ProcedureIndex) -> None: ...
    def add_undefined_procedure(
        self,
        index: ProcedureIndex,
        title: t.Optional[str] = None,
    ) -> None: ...
    def add_constant_procedure(
        self,
        index: ProcedureIndex,
        value: t.Optional[float] = None,
    ) -> None: ...
    def add_getattr_procedure(self, index: ProcedureIndex, attr: str) -> None: ...
    def add_varname_procedure(
        self,
        index: ProcedureIndex,
        varname: str,
        default: float,
    ) -> None: ...
    def add_formula_procedure(
        self,
        index: ProcedureIndex,
        code: str,
        procedures: t.Sequence[ProcedureIndex],
    ) -> None: ...
    def add_ceil_procedure(self, index: ProcedureIndex, proc: ProcedureIndex) -> None: ...
    def add_floor_procedure(self, index: ProcedureIndex, proc: ProcedureIndex) -> None: ...
    def add_round_procedure(
        self,
        index: ProcedureIndex,
        digits: int,
        proc: ProcedureIndex,
    ) -> None: ...
    def add_setenv_procedure(
        self,
        index: ProcedureIndex,
        env: t.Mapping[str, float],
        proc: ProcedureIndex,
    ) -> None: ...
    def add_setfallback_procedure(
        self,
        index: ProcedureIndex,
        env: t.Mapping[str, float],
        proc: ProcedureIndex,
    ) -> None: ...
    def add_branching_procedure_with_validity_pred(
        self,
        index: ProcedureIndex,
        branches: t.Sequence[t.Tuple[datetime, datetime, ProcedureIndex]],
        otherwise: t.Optional[ProcedureIndex],
        backtrack: bool,
    ) -> None: ...
    def add_branching_procedure_with_execution_pred(
        self,
        index: ProcedureIndex,
        branches: t.Sequence[t.Tuple[datetime, datetime, ProcedureIndex]],
        otherwise: t.Optional[ProcedureIndex],
        backtrack: bool,
    ) -> None: ...
    def add_branching_procedure_with_quantity_pred(
        self,
        index: ProcedureIndex,
        branches: t.Sequence[t.Tuple[float, float, ProcedureIndex]],
        otherwise: t.Optional[ProcedureIndex],
        backtrack: bool,
    ) -> None: ...
    def add_branching_procedure_with_match_attr_pred(
        self,
        index: ProcedureIndex,
        branches: t.Sequence[t.Tuple[str, TEq, ProcedureIndex]],
        otherwise: t.Optional[ProcedureIndex],
        backtrack: bool,
    ) -> None: ...
    def add_branching_procedure_with_attr_in_range_pred(
        self,
        index: ProcedureIndex,
        branches: t.Sequence[t.Tuple[str, TOrd, TOrd, ProcedureIndex]],
        otherwise: t.Optional[ProcedureIndex],
        backtrack: bool,
    ) -> None: ...
    def add_matrix_procedure(self, index: ProcedureIndex, matrix: MatrixProcedure) -> None: ...
    def execute(self, demand: UnitaryDemand, undefined: Result) -> Result: ...
    def execute_many(
        self,
        demand: t.Sequence[UnitaryDemand],
        undefined: Result,
    ) -> t.Sequence[Result]: ...

class ExternalObject:
    def __init__(self, name: str, id: int) -> None: ...
    @classmethod
    def from_tuple(cls, desc: ExternalObjectDesc) -> ExternalObject: ...
    @classmethod
    def from_reference_string(cls, refstr: str) -> ExternalObject: ...

ExternalObjectDesc = t.Tuple[str, int]
Value = t.Union[datetime, timedelta, float, str, ExternalObject, ExternalObjectDesc]

class UnitaryDemand:
    def __init__(
        self,
        date: datetime,
        quantity: float,
        start_date: datetime,
        attrs: t.Mapping[str, Value],
    ) -> None: ...
    @classmethod
    def default(cls) -> UnitaryDemand: ...
    def attr(self, attr: str) -> t.Optional[Value]: ...
    def replace_attr(self, attr: str, value: Value) -> UnitaryDemand: ...

class NullDemand: ...

class MatrixProcedure:
    def add_row(self, row: MatrixRow, result: t.Union[float, int, str]): ...

class MatrixRow:
    def add_condition_demand_date_in_range(self, start: datetime, end: datetime): ...
    def add_condition_demand_date_is(self, date: datetime): ...
    def add_condition_start_date_in_range(self, start: datetime, end: datetime): ...
    def add_condition_start_date_is(self, date: datetime): ...
    def add_condition_quantity_in_range(self, min_: float, max_: float): ...
    def add_condition_quantity_is(self, quantity: float): ...
    def add_condition_attr_in_range(self, attr: str, lower: Value, upper: Value): ...
    def add_condition_attr_is(self, attr: str, value: Value): ...

def float_round(
    value: float,
    precision_digits: int = 2,
    rounding_method: t.Literal["UP", "DOWN", "HALF-UP"] = "HALF-UP",
) -> float: ...
