from dataclasses import dataclass
from typing import Any

# ---- expressions ----
@dataclass
class Num:       value: str; is_float: bool; line: int = 0; ty: Any = None
@dataclass
class Str:       raw: str; single: bool; line: int = 0; ty: Any = None
@dataclass
class Bool:      value: bool; line: int = 0; ty: Any = None
@dataclass
class Name:      name: str; line: int = 0; ty: Any = None
@dataclass
class BinOp:     op: str; left: Any; right: Any; line: int = 0; ty: Any = None
@dataclass
class CompareChain: operands: list; operators: list; line: int = 0; ty: Any = None
@dataclass
class UnaryOp:   op: str; operand: Any; line: int = 0; ty: Any = None
@dataclass
class Call:      func: str; args: list; line: int = 0; ty: Any = None
@dataclass
class Index:     obj: Any; index: Any; line: int = 0; ty: Any = None
@dataclass
class ListLit:   items: list; line: int = 0; ty: Any = None
@dataclass
class DictLit:   pairs: list; line: int = 0; ty: Any = None

# ---- statements ----
@dataclass
class Assign:    target: Any; value: Any; line: int = 0
@dataclass
class If:        cond: Any; body: list; orelse: list; line: int = 0
@dataclass
class While:     cond: Any; body: list; line: int = 0
@dataclass
class For:       var: str; iter: Any; body: list; line: int = 0
@dataclass
class Def:       name: str; params: list; body: list; line: int = 0
@dataclass
class Return:    value: Any; line: int = 0
@dataclass
class ExprStmt:  expr: Any; line: int = 0
@dataclass
class Break:     line: int = 0
@dataclass
class Continue:  line: int = 0
@dataclass
class Pass:      line: int = 0