from ast_nodes import *
from pytypes import *
from errors import CompileError

# name: (allowed arg counts or None, allowed arg kinds per position, result(types, line))
def _append(ts, ln):
    ts[0].args[0] = unify(ts[0].args[0], ts[1], ln, "append")   # refines [] element type
    return NONE

def _contains(ts, ln):
    container, item = ts
    if container.kind == "str":
        unify(STR, item, ln, "contains")
    elif container.kind == "list":
        container.args[0] = unify(container.args[0], item, ln, "contains")
    elif container.kind == "dict":
        container.args[0] = unify(container.args[0], item, ln, "contains")
    else:
        raise CompileError("TypeError", f"contains() does not accept {container}", ln)
    return BOOL

def _sum(ts, ln):
    element = ts[0].args[0]
    if element.kind not in NUMERIC and element.kind != "?":
        raise CompileError("TypeError", f"sum() requires a list of numbers, got {ts[0]}", ln)
    return element

BUILTINS = {
    "print":  (None, None,                         lambda ts, ln: NONE),
    "len":    ((1,), [("list", "dict", "str")],    lambda ts, ln: INT),
    "input":  ((0, 1), [("str",)],                 lambda ts, ln: STR),
    "sqrt":   ((1,), [NUMERIC],                    lambda ts, ln: FLOAT),
    "abs":    ((1,), [NUMERIC],                    lambda ts, ln: ts[0]),
    "min":    ((2,), [NUMERIC, NUMERIC],           lambda ts, ln: unify(ts[0], ts[1], ln, "min")),
    "max":    ((2,), [NUMERIC, NUMERIC],           lambda ts, ln: unify(ts[0], ts[1], ln, "max")),
    "int":    ((1,), [("int", "float", "str", "bool")], lambda ts, ln: INT),
    "float":  ((1,), [("int", "float", "str")],    lambda ts, ln: FLOAT),
    "str":    ((1,), None,                         lambda ts, ln: STR),
    "round":  ((1,), [NUMERIC],                    lambda ts, ln: INT),
    "pow":    ((2,), [NUMERIC, NUMERIC],           lambda ts, ln: FLOAT),
    "append": ((2,), [("list",), None],            _append),
    "keys":   ((1,), [("dict",)],                  lambda ts, ln: list_of(ts[0].args[0])),
    "upper":  ((1,), [("str",)],                   lambda ts, ln: STR),
    "lower":  ((1,), [("str",)],                   lambda ts, ln: STR),
    "split":  ((1, 2), [("str",), ("str",)],       lambda ts, ln: list_of(STR)),
    "contains": ((2,), None,                       _contains),
    "sum":    ((1,), [("list",)],                  _sum),
    "sorted": ((1,), [("list",)],                  lambda ts, ln: ts[0]),
    # range is handled inside For.
}

class FuncInfo:
    def __init__(self, node):
        self.node, self.state = node, "new"      # new -> busy -> done
        self.params, self.ret, self.locals = [], None, {}

class Scope:
    def __init__(self, parent=None):
        self.vars, self.parent = {}, parent
    def lookup(self, n):
        s = self
        while s:
            if n in s.vars: return s.vars[n]
            s = s.parent
    def owner(self, n):                              # the scope that declares n
        s = self
        while s:
            if n in s.vars: return s
            s = s.parent

class Inferer:
    def __init__(self):
        self.funcs, self.globals = {}, Scope()
        self.scope, self.fn, self.loops = self.globals, None, 0

    def run(self, prog):
        for s in prog:                               # register functions first
            if isinstance(s, Def):
                if s.name in self.funcs or s.name in BUILTINS:
                    raise CompileError("NameError", f"'{s.name}' already defined", s.line)
                self.funcs[s.name] = FuncInfo(s)
        for s in prog:
            if not isinstance(s, Def): self.stmt(s)
        self.check_uncalled()
        return self

    # ---- names-only check for functions that are never called (their types are unknown) ----
    def check_uncalled(self):
        for f in self.funcs.values():
            if f.state == "new":
                self.r_block(f.node.body, set(f.node.params))

    def r_block(self, body, known):
        for s in body: self.r_stmt(s, known)

    def r_stmt(self, s, known):
        k = type(s).__name__
        if k == "Let":
            self.r_expr(s.value, known); known.add(s.name)
        elif k == "Assign":
            self.r_expr(s.value, known)
            if isinstance(s.target, Name): self.r_name(s.target, known, assign=True)
            else: self.r_expr(s.target, known)
        elif k == "If":
            self.r_expr(s.cond, known); self.r_block(s.body, known); self.r_block(s.orelse, known)
        elif k == "While":
            self.r_expr(s.cond, known); self.r_block(s.body, known)
        elif k == "For":
            self.r_expr(s.iter, known); known.add(s.var); self.r_block(s.body, known)
        elif k == "Return":
            if s.value is not None: self.r_expr(s.value, known)
        elif k == "ExprStmt":
            self.r_expr(s.expr, known)
        elif k == "Def":
            self.s_Def(s)

    def r_name(self, e, known, assign=False):
        if e.name in known or self.globals.lookup(e.name) is not None: return
        if assign:
            raise CompileError("NameError",
                f"'{e.name}' is not declared (declare it first: let {e.name} = ...)", e.line)
        raise CompileError("NameError", f"name '{e.name}' is not defined", e.line)

    def r_expr(self, e, known):
        k = type(e).__name__
        if k == "Name": self.r_name(e, known)
        elif k == "BinOp": self.r_expr(e.left, known); self.r_expr(e.right, known)
        elif k == "UnaryOp": self.r_expr(e.operand, known)
        elif k == "CompareChain":
            for o in e.operands: self.r_expr(o, known)
        elif k == "Call":
            if e.func not in self.funcs and e.func not in BUILTINS and e.func != "range":
                raise CompileError("NameError", f"function '{e.func}' is not defined", e.line)
            for a in e.args: self.r_expr(a, known)
        elif k == "Index": self.r_expr(e.obj, known); self.r_expr(e.index, known)
        elif k == "ListLit":
            for x in e.items: self.r_expr(x, known)
        elif k == "DictLit":
            for kx, vx in e.pairs: self.r_expr(kx, known); self.r_expr(vx, known)

    # ---- statements ----
    def stmt(self, s): getattr(self, "s_" + type(s).__name__)(s)
    def block(self, b):
        for s in b: self.stmt(s)

    def cond(self, e):
        t = self.expr(e)
        if t.kind not in ("bool", "int", "?"):
            raise CompileError("TypeError", f"condition must be bool or int, got {t}", e.line)

    def declare(self, name, t, line):
        cur = self.scope.vars.get(name)
        if cur is None:
            self.scope.vars[name] = t
        elif cur.kind == "float" and t.kind == "int":
            pass                                     # an int may be stored in a float variable
        else:
            self.scope.vars[name] = unify(cur, t, line, f"variable '{name}'")

    def s_Let(self, s):
        vt = self.expr(s.value)                      # evaluated first: 'let a = a + 1' is a NameError
        if vt.kind == "none":
            raise CompileError("TypeError", "cannot assign a value of type none", s.line)
        if s.name in self.scope.vars:
            raise CompileError("NameError", f"'{s.name}' is already declared in this scope", s.line)
        self.scope.vars[s.name] = vt

    def s_Assign(self, s):
        vt = self.expr(s.value)
        if vt.kind == "none":
            raise CompileError("TypeError", "cannot assign a value of type none", s.line)
        t = s.target
        if isinstance(t, Name):
            sc = self.scope.owner(t.name)
            if sc is None:
                raise CompileError("NameError",
                    f"'{t.name}' is not declared (declare it first: let {t.name} = ...)", s.line)
            cur = sc.vars[t.name]
            if not (cur.kind == "float" and vt.kind == "int"):   # an int may go into a float variable
                sc.vars[t.name] = unify(cur, vt, s.line, f"variable '{t.name}'")
            t.ty = sc.vars[t.name]
        else:
            ot, it = self.expr(t.obj), self.expr(t.index)
            if ot.kind == "list":
                unify(INT, it, s.line, "list index")
                ot.args[0] = unify(ot.args[0], vt, s.line, "list element")
            elif ot.kind == "dict":                  # d[k] = v can create new keys
                ot.args[0] = unify(ot.args[0], it, s.line, "dict key")
                ot.args[1] = unify(ot.args[1], vt, s.line, "dict value")
            else:
                raise CompileError("TypeError", f"{ot} does not support item assignment", s.line)
            t.ty = vt

    def s_If(self, s):
        self.cond(s.cond); self.block(s.body); self.block(s.orelse)

    def s_While(self, s):
        self.cond(s.cond); self.loops += 1; self.block(s.body); self.loops -= 1

    def s_For(self, s):
        it = s.iter
        if isinstance(it, Call) and it.func == "range":
            if len(it.args) not in (1, 2, 3):
                raise CompileError("TypeError", "range() takes 1 to 3 arguments", s.line)
            for a in it.args: unify(INT, self.expr(a), s.line, "range argument")
            vt = it.ty = INT
        else:
            t = self.expr(it)
            if   t.kind == "list": vt = t.args[0]
            elif t.kind == "str":  vt = STR
            elif t.kind == "dict": vt = t.args[0]
            else: raise CompileError("TypeError", f"cannot iterate over {t}", s.line)
        self.declare(s.var, vt, s.line)
        self.loops += 1; self.block(s.body); self.loops -= 1

    def s_Def(self, s):
        raise CompileError("SyntaxError", "nested functions are not supported", s.line)

    def s_Return(self, s):
        if self.fn is None:
            raise CompileError("SyntaxError", "'return' outside function", s.line)
        t = NONE if s.value is None else self.expr(s.value)
        f = self.fn
        f.ret = t if f.ret is None else unify(f.ret, t, s.line, f"return type of {f.node.name}()")

    def s_Break(self, s):
        if not self.loops: raise CompileError("SyntaxError", "'break' outside loop", s.line)
    def s_Continue(self, s):
        if not self.loops: raise CompileError("SyntaxError", "'continue' outside loop", s.line)
    def s_Pass(self, s): pass
    def s_ExprStmt(self, s): self.expr(s.expr)

    # ---- expressions ----
    def expr(self, e):
        e.ty = getattr(self, "e_" + type(e).__name__)(e)
        return e.ty

    def e_Num(self, e):
        if not e.is_float and int(e.value) > 9223372036854775807:
            raise CompileError("ValueError",
                "integer literal too large (maximum is 9223372036854775807)", e.line)
        return FLOAT if e.is_float else INT
    def e_Str(self, e):  return STR
    def e_Bool(self, e): return BOOL

    def e_Name(self, e):
        t = self.scope.lookup(e.name)
        if t is None:
            raise CompileError("NameError", f"name '{e.name}' is not defined", e.line)
        return t

    def e_UnaryOp(self, e):
        t = self.expr(e.operand)
        if e.op == "not": return BOOL
        if t.kind not in NUMERIC: raise CompileError("TypeError", f"cannot negate {t}", e.line)
        return t

    def e_BinOp(self, e):
        l, r, op = self.expr(e.left), self.expr(e.right), e.op
        if l.kind == "?": l = r                      # recursive-call placeholder
        if r.kind == "?": r = l
        if op in ("and", "or"): return BOOL
        if op in ("==", "!=", "<", ">", "<=", ">="):
           self.check_comparison(l, r, op, e.line)

           return BOOL
        if op == "+" and l.kind in ("str", "list"):
            return unify(l, r, e.line, "'+'")
        if l.kind not in NUMERIC or r.kind not in NUMERIC:
            raise CompileError("TypeError", f"unsupported operand types for '{op}': {l} and {r}", e.line)
        both_int = l.kind == "int" and r.kind == "int"
        if op == "/":  return FLOAT
        if op in ("//", "%"):
            return INT if both_int else FLOAT
        return INT if both_int else FLOAT            # + - * **

    def e_CompareChain(self, e):
        types = [self.expr(operand) for operand in e.operands]
        for left, right, op in zip(types, types[1:], e.operators):
            if left.kind == "?": left = right
            if right.kind == "?": right = left
            self.check_comparison(left, right, op, e.line)
        return BOOL

    @staticmethod
    def check_comparison(left, right, op, line):
        if not (left.kind in NUMERIC and right.kind in NUMERIC):
            unify(left, right, line, f"comparison '{op}'")

    def e_Index(self, e):
        ot, it = self.expr(e.obj), self.expr(e.index)
        if ot.kind == "list": unify(INT, it, e.line, "list index"); return ot.args[0]
        if ot.kind == "str":  unify(INT, it, e.line, "string index"); return STR
        if ot.kind == "dict":
            ot.args[0] = unify(ot.args[0], it, e.line, "dict key"); return ot.args[1]
        raise CompileError("TypeError", f"{ot} is not indexable", e.line)

    def e_ListLit(self, e):
        el = UNKNOWN
        for x in e.items: el = unify(el, self.expr(x), e.line, "list element")
        return list_of(el)

    def e_DictLit(self, e):
        k = v = UNKNOWN
        for kx, vx in e.pairs:
            k = unify(k, self.expr(kx), e.line, "dict key")
            v = unify(v, self.expr(vx), e.line, "dict value")
        return dict_of(k, v)

    def e_Call(self, e):
        if e.func in self.funcs: return self.call_user(e)
        if e.func not in BUILTINS:
            raise CompileError("NameError", f"function '{e.func}' is not defined", e.line)
        arity, kinds, result = BUILTINS[e.func]
        ts = [self.expr(a) for a in e.args]
        if arity is not None and len(ts) not in arity:
            raise CompileError("TypeError", f"{e.func}() takes {arity} argument(s), got {len(ts)}", e.line)
        for t, allowed in zip(ts, kinds or []):
            if allowed is not None and t.kind not in allowed and t.kind != "?":
                raise CompileError("TypeError", f"{e.func}() does not accept {t}", e.line)
        return result(ts, e.line)

    def call_user(self, e):
        f = self.funcs[e.func]
        argtys = [self.expr(a) for a in e.args]
        if len(argtys) != len(f.node.params):
            raise CompileError("TypeError",
                f"{e.func}() takes {len(f.node.params)} argument(s), got {len(argtys)}", e.line)
        for a, t in zip(e.args, argtys):
            if t.kind in ("list", "dict") and not isinstance(a, (Name, Index)):
                raise CompileError("TypeError",
                    f"{e.func}(): put the list/dict in a variable first, then pass the variable", e.line)
        if f.state == "new":
            self.infer_fn(f, argtys)
        else:                                        # busy (recursion) or done: must match
            for p, a in zip(f.params, argtys):
                unify(p, a, e.line, f"argument to {e.func}() (functions are monomorphic)")
        return f.ret if f.ret is not None else UNKNOWN

    def infer_fn(self, f, argtys):
        f.state, f.params = "busy", argtys
        saved = (self.scope, self.fn, self.loops)
        self.scope, self.fn, self.loops = Scope(self.globals), f, 0
        for n, t in zip(f.node.params, argtys): self.scope.vars[n] = t
        self.block(f.node.body)
        if f.ret is None: f.ret = NONE
        f.locals, f.state = self.scope.vars, "done"
        self.scope, self.fn, self.loops = saved