import re
from dataclasses import dataclass
from errors import CompileError

@dataclass
class Token:
    kind: str
    value: str
    line: int

KEYWORDS = {"def", "return", "if", "elif", "else", "while", "for", "in",
            "and", "or", "not", "True", "False", "break", "continue", "pass"}

TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in [
    ("FLOAT",   r"\d+\.\d+"),
    ("INT",     r"\d+"),
    ("STRING",  r'"(?:\\["nt]|[^"\\\n])*"|\'(?:\\["nt]|[^\'\\\n])*\''),
    ("NAME",    r"[A-Za-z_]\w*"),
    ("OP",      r"\+=|-=|\*=|/=|==|!=|<=|>=|//|\*\*|[+\-*/%<>=]"),
    ("PUNCT",   r"[()\[\]{},:]"),
    ("SKIP",    r"[ \t]+"),
    ("COMMENT", r"#.*"),
    ("BAD",     r"."),
]))

def lex(src: str) -> list[Token]:
    toks, indents = [], [0]
    bracket_depth = 0
    for lineno, raw in enumerate(src.splitlines(), 1):
        stripped = raw.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        continuation = bracket_depth > 0
        if not continuation and "\t" in raw[: len(raw) - len(stripped)]:
            raise CompileError("IndentationError", "use spaces, not tabs", lineno)
        width = len(raw) - len(stripped)
        if not continuation:
            if width > indents[-1]:
                indents.append(width)
                toks.append(Token("INDENT", "", lineno))
            else:
                while width < indents[-1]:
                    indents.pop()
                    toks.append(Token("DEDENT", "", lineno))
                if width != indents[-1]:
                    raise CompileError("IndentationError", "inconsistent dedent", lineno)
        for m in TOKEN_RE.finditer(raw, width):
            kind, val = m.lastgroup, m.group()
            if kind in ("SKIP", "COMMENT"):
                continue
            if kind == "BAD":
                raise CompileError("SyntaxError", f"unexpected character {val!r}", lineno)
            if kind == "NAME" and val in KEYWORDS:
                kind = "KW"
            toks.append(Token(kind, val, lineno))
            if kind == "PUNCT":
                if val in "([{":
                    bracket_depth += 1
                elif val in ")]}" and bracket_depth:
                    bracket_depth -= 1
        if bracket_depth == 0:
            toks.append(Token("NEWLINE", "", lineno))
    last = toks[-1].line if toks else 1
    while len(indents) > 1:
        indents.pop()
        toks.append(Token("DEDENT", "", last))
    toks.append(Token("EOF", "", last))
    return toks 