from errors import CompileError

class Ty:
    def __init__(self, kind, *args):
        self.kind, self.args = kind, list(args)
    def __eq__(self, o):
        return isinstance(o, Ty) and self.kind == o.kind and self.args == o.args
    def __repr__(self):
        return self.kind if not self.args else f"{self.kind}[{', '.join(map(repr, self.args))}]"

INT, FLOAT, STR, BOOL, NONE, UNKNOWN = (Ty(k) for k in ("int", "float", "str", "bool", "none", "?"))
NUMERIC = ("int", "float")
def list_of(t):    return Ty("list", t)
def dict_of(k, v): return Ty("dict", k, v)

def unify(a, b, line, ctx=""):
    """Check a and b are compatible; fill in '?' slots (e.g. element type of [])."""
    if a.kind == "?": return b
    if b.kind == "?": return a
    if a.kind != b.kind:
        raise CompileError("TypeError", f"{ctx}: expected {a}, got {b}", line)
    for i, (x, y) in enumerate(zip(a.args, b.args)):
        merged = unify(x, y, line, ctx)
        a.args[i] = b.args[i] = merged
    return a    