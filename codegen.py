from ast_nodes import *
from errors import CompileError

RUNTIME = r'''#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <cctype>
#include <string>
#include <cmath>
#include <sstream>
#include <stdexcept>

struct PyError : std::runtime_error { using std::runtime_error::runtime_error; };
static long long py_line = 0;   // source line of the statement being executed
static int py_depth = 0;        // current call depth (guards against runaway recursion)
struct PyDepth {
    PyDepth() { if (py_depth >= 1000) throw PyError("RecursionError: maximum recursion depth exceeded");
                ++py_depth; }
    ~PyDepth() { --py_depth; }
};

// ---- indexing: negative indices + bounds checks ----
template<class T> T& idx(std::vector<T>& v, long long i) {
    long long n = (long long)v.size(); if (i < 0) i += n;
    if (i < 0 || i >= n) throw PyError("IndexError: list index out of range");
    return v[i];
}
template<class T> const T& idx(const std::vector<T>& v, long long i) {
    long long n = (long long)v.size(); if (i < 0) i += n;
    if (i < 0 || i >= n) throw PyError("IndexError: list index out of range");
    return v[i];
}
inline std::string idx(const std::string& s, long long i) {
    long long n = (long long)s.size(); if (i < 0) i += n;
    if (i < 0 || i >= n) throw PyError("IndexError: string index out of range");
    return std::string(1, s[i]);
}
template<class K, class V> const V& key(const std::map<K, V>& m, const K& k) {
    auto it = m.find(k);
    if (it == m.end()) throw PyError("KeyError: key not found");
    return it->second;
}
template<class T> bool py_contains(const std::vector<T>& v, const T& x) {
    return std::find(v.begin(), v.end(), x) != v.end(); }
template<class K, class V> bool py_contains(const std::map<K, V>& m, const K& k) {
    return m.find(k) != m.end(); }
inline bool py_contains(const std::string& s, const std::string& part) {
    return s.find(part) != std::string::npos; }

// ---- arithmetic ----
inline double py_div(double a, double b) {
    if (b == 0) throw PyError("ZeroDivisionError: division by zero"); return a / b; }
inline long long py_floordiv(long long a, long long b) {
    if (b == 0) throw PyError("ZeroDivisionError: integer division by zero");
    long long q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) --q; return q; }
inline long long py_mod(long long a, long long b) {
    if (b == 0) throw PyError("ZeroDivisionError: modulo by zero");
    long long r = a % b; if (r != 0 && ((r < 0) != (b < 0))) r += b; return r; }
inline double py_floordiv(double a, double b) {
    if (b == 0) throw PyError("ZeroDivisionError: float floor division by zero");
    return std::floor(a / b); }
inline double py_mod(double a, double b) {
    if (b == 0) throw PyError("ZeroDivisionError: float modulo by zero");
    double r = std::fmod(a, b);
    if (r != 0 && ((r < 0) != (b < 0))) r += b;
    return r == 0 ? std::copysign(0.0, b) : r; }
inline long long py_ipow(long long b, long long e) {
    if (e < 0) throw PyError("ValueError: negative exponent (use float operands)");
    long long r = 1; while (e) { if (e & 1) r *= b; b *= b; e >>= 1; } return r; }

// ---- to-string (used by str() and print) ----
inline std::string py_str(const std::string& s) { return s; }
inline std::string py_str(bool b) { return b ? "True" : "False"; }
inline std::string py_str(long long v) { return std::to_string(v); }
inline std::string py_str(double d) {
    if (std::isnan(d)) return "nan";
    if (std::isinf(d)) return d < 0 ? "-inf" : "inf";
    std::string s;
    for (int p = 15; p <= 17; ++p) {             // shortest text that reads back exactly
        std::ostringstream o; o.precision(p); o << d; s = o.str();
        if (std::stod(s) == d) break; }
    if (s.find_first_of(".en") == std::string::npos) s += ".0"; return s; }
template<class T> std::string py_str(const std::vector<T>& v);
template<class K, class V> std::string py_str(const std::map<K, V>& m);
inline std::string py_repr(const std::string& s) { return "'" + s + "'"; }
template<class T> std::string py_repr(const T& v) { return py_str(v); }
template<class T> std::string py_str(const std::vector<T>& v) {
    std::string s = "[";
    for (size_t i = 0; i < v.size(); ++i) { if (i) s += ", "; s += py_repr(v[i]); }
    return s + "]"; }
template<class K, class V> std::string py_str(const std::map<K, V>& m) {
    std::string s = "{"; bool first = true;
    for (auto& kv : m) { if (!first) s += ", "; first = false;
        s += py_repr(kv.first) + ": " + py_repr(kv.second); }
    return s + "}"; }

// ---- built-ins ----
inline void py_print() { std::cout << '\n'; }
template<class T, class... R> void py_print(const T& a, const R&... r) {
    std::cout << py_str(a); ((std::cout << ' ' << py_str(r)), ...); std::cout << '\n'; }
inline std::string py_input(const std::string& prompt = "") {
    std::cout << prompt << std::flush; std::string s;
    if (!std::getline(std::cin, s)) throw PyError("EOFError: no input available"); return s; }
inline long long py_len(const std::string& s) { return (long long)s.size(); }
template<class T> long long py_len(const std::vector<T>& v) { return (long long)v.size(); }
template<class K, class V> long long py_len(const std::map<K, V>& m) { return (long long)m.size(); }
inline std::string py_upper(std::string s) {
    for (char& c : s) c = (char)std::toupper((unsigned char)c); return s; }
inline std::string py_lower(std::string s) {
    for (char& c : s) c = (char)std::tolower((unsigned char)c); return s; }
inline std::vector<std::string> py_split(const std::string& s) {
    std::istringstream in(s); std::vector<std::string> out; std::string part;
    while (in >> part) out.push_back(part); return out; }
inline std::vector<std::string> py_split(const std::string& s, const std::string& sep) {
    if (sep.empty()) throw PyError("ValueError: empty separator");
    std::vector<std::string> out; size_t start = 0, pos;
    while ((pos = s.find(sep, start)) != std::string::npos) {
        out.push_back(s.substr(start, pos - start)); start = pos + sep.size(); }
    out.push_back(s.substr(start)); return out; }
template<class T> T py_sum(const std::vector<T>& v) {
    T total{}; for (const T& x : v) total += x; return total; }
template<class T> std::vector<T> py_sorted(std::vector<T> v) {
    std::sort(v.begin(), v.end()); return v; }
inline double py_sqrt(double x) {
    if (x < 0) throw PyError("ValueError: math domain error"); return std::sqrt(x); }
template<class T> T py_abs(T x) { return x < 0 ? -x : x; }
template<class T> T py_min(T a, T b) { return b < a ? b : a; }
template<class T> T py_max(T a, T b) { return a < b ? b : a; }
inline long long py_int(const std::string& s) {
    try { size_t p; long long v = std::stoll(s, &p); if (p != s.size()) throw 1; return v; }
    catch (...) { throw PyError("ValueError: invalid literal for int(): '" + s + "'"); } }
inline long long py_int(double d) { return (long long)d; }
inline long long py_int(long long v) { return v; }
inline long long py_int(bool b) { return b ? 1 : 0; }
inline double py_float(const std::string& s) {
    try { size_t p; double v = std::stod(s, &p); if (p != s.size()) throw 1; return v; }
    catch (...) { throw PyError("ValueError: could not convert string to float: '" + s + "'"); } }
inline double py_float(double d) { return d; }
inline double py_float(long long v) { return (double)v; }
inline long long py_round(double x) { return (long long)std::nearbyint(x); }
inline double py_pow(double a, double b) { return std::pow(a, b); }
template<class T> void py_append(std::vector<T>& v, const T& x) { v.push_back(x); }
template<class T> std::vector<T> py_concat(std::vector<T> a, const std::vector<T>& b) {
    a.insert(a.end(), b.begin(), b.end()); return a; }
template<class K, class V> std::vector<K> py_keys(const std::map<K, V>& m) {
    std::vector<K> out; for (auto& kv : m) out.push_back(kv.first); return out; }

'''

CPP_BUILTIN = {"print": "py_print", "len": "py_len", "input": "py_input", "sqrt": "py_sqrt",
               "abs": "py_abs", "min": "py_min", "max": "py_max", "int": "py_int",
               "float": "py_float", "str": "py_str", "round": "py_round", "pow": "py_pow",
               "append": "py_append", "keys": "py_keys", "upper": "py_upper",
               "lower": "py_lower", "split": "py_split", "contains": "py_contains",
               "sum": "py_sum", "sorted": "py_sorted"}

def vn(n): return "v_" + n          # mangle user names so they never clash with C++ keywords
def fn(n): return "f_" + n

def cpp_type(t, line=0):
    k = t.kind
    if k == "int":   return "long long"
    if k == "float": return "double"
    if k == "str":   return "std::string"
    if k == "bool":  return "bool"
    if k == "none":  return "void"
    if k == "list":  return f"std::vector<{cpp_type(t.args[0], line)}>"
    if k == "dict":  return f"std::map<{cpp_type(t.args[0], line)}, {cpp_type(t.args[1], line)}>"
    raise CompileError("TypeError", "could not infer a type (e.g. an empty list that is never filled)", line)

class CodeGen:
    def __init__(self, inf):
        self.inf, self.out, self.depth, self.n = inf, [], 0, 0

    def w(self, line): self.out.append("    " * self.depth + line)

    def generate(self, prog):
        self.out.append(RUNTIME)
        for name, t in self.inf.globals.vars.items():          # hoisted module variables
            self.w(f"{cpp_type(t)} {vn(name)}{{}};")
        done = [f for f in self.inf.funcs.values() if f.state == "done"]  # uncalled fns skipped
        for f in done: self.w(self.sig(f) + ";")
        for f in done: self.func(f)
        self.w("int main() {"); self.depth += 1
        self.w("try {"); self.depth += 1
        for s in prog:
            if not isinstance(s, Def): self.stmt(s)
        self.depth -= 1
        self.w('} catch (const PyError& e) { std::cerr << "Runtime error (line " << py_line << "): " << e.what() << std::endl; return 1; }')
        self.w("return 0;"); self.depth -= 1; self.w("}")
        return "\n".join(self.out)

    # ---- functions ----
    def sig(self, f):
        ps = []
        for name, t in zip(f.node.params, f.params):
            ref = "&" if t.kind in ("list", "dict") else ""   # containers by reference
            ps.append(f"{cpp_type(t, f.node.line)}{ref} {vn(name)}")
        return f"{cpp_type(f.ret, f.node.line)} {fn(f.node.name)}({', '.join(ps)})"

    def func(self, f):
        self.w(self.sig(f) + " {"); self.depth += 1
        self.w("PyDepth _depth_guard;")
        for name, t in f.locals.items():                      # hoist locals (Python function scope)
            if name not in f.node.params:
                self.w(f"{cpp_type(t, f.node.line)} {vn(name)}{{}};")
        for s in f.node.body: self.stmt(s)
        if f.ret.kind != "none":
            self.w('throw PyError("RuntimeError: function ended without return");')
        self.depth -= 1; self.w("}")

    # ---- statements ----
    def stmt(self, s):
        self.w(f"py_line = {s.line};")
        getattr(self, "g_" + type(s).__name__)(s)
    def body(self, b):
        self.depth += 1
        for s in b: self.stmt(s)
        self.depth -= 1

    def g_Assign(self, s):
        t, v = s.target, self.ex(s.value)
        if isinstance(t, Name):
            self.w(f"{vn(t.name)} = {v};")
        elif t.obj.ty.kind == "list":
            self.w(f"idx({self.ex(t.obj)}, {self.ex(t.index)}) = {v};")
        else:
            self.w(f"{self.ex(t.obj)}[{self.ex(t.index)}] = {v};")

    def g_Let(self, s):                              # variable already declared (hoisted) above
        self.w(f"{vn(s.name)} = {self.ex(s.value)};")

    def g_If(self, s):
        self.w(f"if ({self.ex(s.cond)}) {{"); self.body(s.body)
        if s.orelse:
            self.w("} else {"); self.body(s.orelse)
        self.w("}")

    def g_While(self, s):
        self.w(f"while ({self.ex(s.cond)}) {{"); self.body(s.body); self.w("}")

    def g_For(self, s):
        k = self.n; self.n += 1; v = vn(s.var); it = s.iter
        if isinstance(it, Call) and it.func == "range":
            if len(it.args) == 1:
                lo, hi, step = "0LL", self.ex(it.args[0]), "1LL"
            elif len(it.args) == 2:
                lo, hi, step = self.ex(it.args[0]), self.ex(it.args[1]), "1LL"
            else:
                lo, hi, step = (self.ex(arg) for arg in it.args)
            self.w(f"long long _start{k} = {lo}, _end{k} = {hi}, _step{k} = {step};")
            self.w(f'if (_step{k} == 0) throw PyError("ValueError: range() arg 3 must not be zero");')
            self.w(f"for (long long _i{k} = _start{k}; _step{k} > 0 ? _i{k} < _end{k} : _i{k} > _end{k}; _i{k} += _step{k}) {{")
            self.depth += 1; self.w(f"{v} = _i{k};")
        else:
            conv = f"std::string(1, _e{k})" if it.ty.kind == "str" else \
                   f"_e{k}.first" if it.ty.kind == "dict" else f"_e{k}"
            self.w(f"for (auto _e{k} : {self.ex(it)}) {{")
            self.depth += 1; self.w(f"{v} = {conv};")
        for x in s.body: self.stmt(x)
        self.depth -= 1; self.w("}")

    def g_Return(self, s):
        self.w("return;" if s.value is None else f"return {self.ex(s.value)};")
    def g_ExprStmt(self, s): self.w(self.ex(s.expr) + ";")
    def g_Break(self, s):    self.w("break;")
    def g_Continue(self, s): self.w("continue;")
    def g_Pass(self, s):     self.w(";")
    def g_Def(self, s):      pass

    # ---- expressions ----
    def ex(self, e): return getattr(self, "x_" + type(e).__name__)(e)

    def x_Num(self, e):  return e.value if e.is_float else e.value + "LL"
    def x_Bool(self, e): return "true" if e.value else "false"
    def x_Name(self, e): return vn(e.name)
    def x_Str(self, e):
        out = []
        for ch in e.raw:
            if ch == "\\": out.append("\\\\")
            elif ch == '"': out.append('\\"')
            elif ch == "\n": out.append("\\n")
            elif ch == "\r": out.append("\\r")
            elif ch == "\t": out.append("\\t")
            elif ch == "\b": out.append("\\b")
            elif ch == "\f": out.append("\\f")
            elif ch == "\v": out.append("\\v")
            elif ch == "\a": out.append("\\a")
            elif ord(ch) < 32 or ch == "\x7f": out.append(f"\\x{ord(ch):02x}")
            else: out.append(ch)
        return 'std::string("' + "".join(out) + '")'
    
    def x_UnaryOp(self, e):
        return f"({'!' if e.op == 'not' else '-'}{self.ex(e.operand)})"

    def x_BinOp(self, e):
        a, b, op = self.ex(e.left), self.ex(e.right), e.op
        if op == "/":  return f"py_div({a}, {b})"
        if op in ("//", "%"):
            if e.ty.kind == "float":
                a, b = f"(double)({a})", f"(double)({b})"
            return f"py_{'floordiv' if op == '//' else 'mod'}({a}, {b})"
        if op == "**":
            ints = e.left.ty.kind == "int" and e.right.ty.kind == "int"
            return f"py_ipow({a}, {b})" if ints else f"std::pow({a}, {b})"
        if op == "+" and e.left.ty.kind == "list": return f"py_concat({a}, {b})"
        op = {"and": "&&", "or": "||"}.get(op, op)
        return f"({a} {op} {b})"

    def x_CompareChain(self, e):
        k = self.n
        self.n += 1
        lines = [f"[&]() {{ auto _cmp{k}_0 = {self.ex(e.operands[0])};",
                 f"auto _cmp{k}_1 = {self.ex(e.operands[1])};"]
        for i, op in enumerate(e.operators[:-1]):
            lines.append(f"if (!(_cmp{k}_{i} {op} _cmp{k}_{i + 1})) return false;")
            lines.append(f"auto _cmp{k}_{i + 2} = {self.ex(e.operands[i + 2])};")
        last = len(e.operators) - 1
        lines.append(f"return (_cmp{k}_{last} {e.operators[last]} _cmp{k}_{last + 1});")
        return "(" + " ".join(lines) + "}())"

    def x_Call(self, e):
        args = ", ".join(self.ex(a) for a in e.args)
        name = fn(e.func) if e.func in self.inf.funcs else CPP_BUILTIN[e.func]
        return f"{name}({args})"

    def x_Index(self, e):
        o, i = self.ex(e.obj), self.ex(e.index)
        return f"key({o}, {i})" if e.obj.ty.kind == "dict" else f"idx({o}, {i})"

    def x_ListLit(self, e):
        return f"{cpp_type(e.ty, e.line)}{{{', '.join(self.ex(x) for x in e.items)}}}"

    def x_DictLit(self, e):
        pairs = ", ".join(f"{{{self.ex(k)}, {self.ex(v)}}}" for k, v in e.pairs)
        return f"{cpp_type(e.ty, e.line)}{{{pairs}}}"