import os, sys, pathlib, subprocess
from errors import CompileError
from lexer import lex
from pyparser import Parser
from infer import Inferer
from codegen import CodeGen

def compile_source(src: str) -> str:
    prog = Parser(lex(src)).program()
    inf = Inferer().run(prog)
    return CodeGen(inf).generate(prog)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("usage: python pylc.py prog.pyl [--run]")
    path = pathlib.Path(args[0])
    if not path.exists():
        sys.exit(f"error: file not found: {path}")
    try:
        cpp = compile_source(path.read_text(encoding="utf-8"))
    except CompileError as e:
        sys.exit(str(e))
    except RecursionError:
        sys.exit("error: program is nested too deeply")
    except Exception as e:                      # never show a Python traceback
        sys.exit(f"InternalError: {type(e).__name__}: {e}")
    out = path.with_suffix(".cpp")
    out.write_text(cpp, encoding="utf-8")
    print(f"wrote {out}")
    if "--run" in sys.argv:
        exe = path.with_suffix(".exe" if os.name == "nt" else "")
        try:
            r = subprocess.run(["g++", "-std=c++17", "-O2", str(out), "-o", str(exe)])
        except FileNotFoundError:
            sys.exit("error: g++ not found - install a C++17 compiler")
        if r.returncode != 0:
            sys.exit("error: the generated C++ did not compile (see messages above)")
        sys.exit(subprocess.run([str(exe.resolve())]).returncode)
if __name__ == "__main__":
    main()