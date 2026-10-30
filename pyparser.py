from ast_nodes import *
from errors import CompileError

_ESCAPE_MAP = {
    "n": "\n", "t": "\t", '"': '"',
}


def _decode_string_literal(literal: str):
    body = literal[1:-1]
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        i += 1
        if i >= len(body):
            raise ValueError("unterminated escape sequence")
        esc = body[i]
        if esc in _ESCAPE_MAP:
            out.append(_ESCAPE_MAP[esc])
            i += 1
            continue
        raise ValueError(f"unsupported escape sequence \\{esc}")
    return "".join(out)


class Parser:
    def __init__(self, toks):
        self.toks, self.i = toks, 0

    # ---- helpers ----
    def peek(self): return self.toks[self.i]
    def next(self):
        t = self.toks[self.i]; self.i += 1; return t
    def at(self, kind, value=None):
        t = self.peek()
        return t.kind == kind and (value is None or t.value == value)
    def accept(self, kind, value=None):
        if self.at(kind, value): return self.next()
    def expect(self, kind, value=None):
        if not self.at(kind, value):
            t = self.peek()
            raise CompileError("SyntaxError",
                f"expected {value or kind}, got {(t.value or t.kind)!r}", t.line)
        return self.next()

    # ---- statements ----
    def program(self):
        out = []
        while not self.at("EOF"):
            out.append(self.stmt())
        return out

    def block(self):
        self.expect("PUNCT", ":"); self.expect("NEWLINE"); self.expect("INDENT")
        body = []
        while not self.at("DEDENT") and not self.at("EOF"):
            body.append(self.stmt())
        self.expect("DEDENT")
        return body

    def stmt(self):
        t = self.peek(); ln = t.line
        if t.kind == "KW":
            if t.value == "def":   return self.def_()
            if t.value == "if":    return self.if_()
            if t.value == "while":
                self.next(); c = self.expr()
                return While(c, self.block(), ln)
            if t.value == "for":
                self.next(); v = self.expect("NAME").value
                self.expect("KW", "in"); it = self.expr()
                return For(v, it, self.block(), ln)
            if t.value == "return":
                self.next()
                v = None if self.at("NEWLINE") else self.expr()
                self.expect("NEWLINE"); return Return(v, ln)
            if t.value in ("break", "continue", "pass"):
                self.next(); self.expect("NEWLINE")
                return {"break": Break, "continue": Continue, "pass": Pass}[t.value](ln)
        if t.kind == "NAME" and t.value == "let" and self.toks[self.i + 1].kind == "NAME":
            raise CompileError("SyntaxError",
                "there is no 'let': create a variable by assigning to it, e.g. x = 5", ln)
        e = self.expr()
        if self.at("OP") and self.peek().value in ("=", "+=", "-=", "*=", "/="):
            op = self.next().value
            if not isinstance(e, (Name, Index)):
                raise CompileError("SyntaxError", "cannot assign to this expression", ln)
            rhs = self.expr()
            if op != "=":
                rhs = BinOp(op[0], e, rhs, ln)       # desugar x += 1  ->  x = x + 1
            self.expect("NEWLINE")
            return Assign(e, rhs, ln)
        self.expect("NEWLINE")
        return ExprStmt(e, ln)

    def def_(self):
        ln = self.next().line
        name = self.expect("NAME").value
        self.expect("PUNCT", "(")
        params = []
        if not self.at("PUNCT", ")"):
            params.append(self.expect("NAME").value)
            while self.accept("PUNCT", ","):
                params.append(self.expect("NAME").value)
        self.expect("PUNCT", ")")
        return Def(name, params, self.block(), ln)

    def if_(self):
        ln = self.next().line                       # consumes 'if' or 'elif'
        cond = self.expr(); body = self.block(); orelse = []
        if self.at("KW", "elif"):
            orelse = [self.if_()]
        elif self.accept("KW", "else"):
            orelse = self.block()
        return If(cond, body, orelse, ln)

    # ---- expressions (one function per precedence level) ----
    def expr(self): return self.or_()

    def or_(self):
        l = self.and_()
        while self.at("KW", "or"):
            ln = self.next().line; l = BinOp("or", l, self.and_(), ln)
        return l

    def and_(self):
        l = self.not_()
        while self.at("KW", "and"):
            ln = self.next().line; l = BinOp("and", l, self.not_(), ln)
        return l

    def not_(self):
        if self.at("KW", "not"):
            ln = self.next().line; return UnaryOp("not", self.not_(), ln)
        return self.cmp()

    def cmp(self):
        operands = [self.arith()]
        operators = []
        line = self.peek().line
        while self.at("OP") and self.peek().value in ("==", "!=", "<", ">", "<=", ">="):
            op = self.next()
            operators.append(op.value)
            operands.append(self.arith())
            line = op.line
        if not operators:
            return operands[0]
        if len(operators) == 1:
            return BinOp(operators[0], operands[0], operands[1], line)
        return CompareChain(operands, operators, line)

    def arith(self):
        l = self.term()
        while self.at("OP") and self.peek().value in ("+", "-"):
            t = self.next(); l = BinOp(t.value, l, self.term(), t.line)
        return l

    def term(self):
        l = self.factor()
        while self.at("OP") and self.peek().value in ("*", "/", "//", "%"):
            t = self.next(); l = BinOp(t.value, l, self.factor(), t.line)
        return l

    def factor(self):
        if self.at("OP", "-"):
            t = self.next(); return UnaryOp("-", self.factor(), t.line)
        return self.power()

    def power(self):
        b = self.postfix()
        if self.at("OP", "**"):
            t = self.next(); return BinOp("**", b, self.factor(), t.line)  # right-assoc
        return b

    def postfix(self):
        e = self.atom()
        while True:
            if self.at("PUNCT", "("):
                if not isinstance(e, Name):
                    raise CompileError("SyntaxError", "only named functions can be called", e.line)
                ln = self.next().line
                e = Call(e.name, self.comma_list(")"), ln)
            elif self.at("PUNCT", "["):
                ln = self.next().line; i = self.expr(); self.expect("PUNCT", "]")
                e = Index(e, i, ln)
            else:
                return e

    def comma_list(self, close):
        items = []
        if not self.at("PUNCT", close):
            items.append(self.expr())
            while self.accept("PUNCT", ","):
                if self.at("PUNCT", close): break
                items.append(self.expr())
        self.expect("PUNCT", close)
        return items

    def atom(self):
        t = self.next()
        if t.kind == "INT":    return Num(t.value, False, t.line)
        if t.kind == "FLOAT":  return Num(t.value, True, t.line)
        if t.kind == "STRING":
            try:
                value = _decode_string_literal(t.value)
            except ValueError as e:
                raise CompileError("SyntaxError", str(e), t.line)
            return Str(value, t.value[0] == "'", t.line)
        if t.kind == "KW" and t.value in ("True", "False"):
            return Bool(t.value == "True", t.line)
        if t.kind == "NAME":   return Name(t.value, t.line)
        if t.kind == "PUNCT" and t.value == "(":
            e = self.expr(); self.expect("PUNCT", ")"); return e
        if t.kind == "PUNCT" and t.value == "[":
            return ListLit(self.comma_list("]"), t.line)
        if t.kind == "PUNCT" and t.value == "{":
            pairs = []
            while not self.at("PUNCT", "}"):
                k = self.expr(); self.expect("PUNCT", ":")
                pairs.append((k, self.expr()))
                if not self.accept("PUNCT", ","): break
            self.expect("PUNCT", "}")
            return DictLit(pairs, t.line)
        raise CompileError("SyntaxError", f"unexpected {(t.value or t.kind)!r}", t.line)