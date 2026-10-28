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
    try:
        cpp = compile_source(path.read_text())
    except CompileError as e:
        sys.exit(str(e))
    out = path.with_suffix(".cpp")
    out.write_text(cpp)
    print(f"wrote {out}")
    if "--run" in sys.argv:
        exe = path.with_suffix(".exe" if os.name == "nt" else "")
        subprocess.run(["g++", "-std=c++17", "-O2", str(out), "-o", str(exe)], check=True)
        subprocess.run([str(exe.resolve())])

if __name__ == "__main__":
    main()