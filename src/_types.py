import typing
from typing_extensions import TypedDict, Literal
from dataclasses import dataclass


class RangeStartEnd(TypedDict):
    line: int
    character: int


class GeneralDiagnosticRange(TypedDict):
    start: RangeStartEnd
    end: RangeStartEnd


class PyrightGeneralDiagnosticItem(TypedDict):
    file: str
    severity: Literal["error", "warning"]
    message: str
    range: GeneralDiagnosticRange
    rule: typing.Optional[str]


@dataclass
class ResultRefItem:
    line: int
    msg: str
    tag: str
    path: str


@dataclass
class ResultDict:
    path: str
    line: int
    column: int
    msg: str
    rule: str
    refs: typing.Optional[typing.List[ResultRefItem]]
