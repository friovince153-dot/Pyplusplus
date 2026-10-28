class CompileError(Exception):
    def __init__(self, kind, msg, line=0):
        super().__init__(f"{kind} (line {line}): {msg}")