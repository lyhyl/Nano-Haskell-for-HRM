from typing import List

header = "-- HUMAN RESOURCE MACHINE PROGRAM --"


def get_rec(p, i, rec):
    vs = []
    if len(p) > i:
        vs.append(p[i])
    if len(p) > rec and p[rec] is not None:
        vs.extend(get_rec(p[rec], i, rec))
    return vs


class Instrument:
    IN = "INBOX"
    OUT = "OUTBOX"
    CPF = "COPYFROM"
    CPT = "COPYTO"
    INC = "BUMPUP"
    DEC = "BUMPDN"
    ADD = "ADD"
    SUB = "SUB"
    JMP = "JUMP"
    JZ = "JUMPZ"
    JN = "JUMPN"
    LAB = "Label"

    def __init__(self, code: str, arg: int = None) -> None:
        self.code = code
        self.arg = arg

    def __repr__(self) -> str:
        pad = " " * 4
        if self.code == Instrument.LAB:
            return f"{self.arg}:"
        elif self.code in [Instrument.IN, Instrument.OUT]:
            return f"{pad}{self.code}"
        elif self.code.startswith("JUMP"):
            return f"{pad}{self.code:9s}{chr(self.arg + ord('a'))}"
        else:
            return f"{pad}{self.code:9s}{self.arg}"


class Context:
    def __init__(self,
                 builtin_funcs: List["Builtin"],
                 builtin_actns: List["Builtin"],
                 funcs: List["Function"]) -> None:
        self.builtin_funcs = {f.name: f for f in builtin_funcs}
        self.builtin_actns = {a.name: a for a in builtin_actns}
        self.funcs = {f.name: f for f in funcs}
        self.vars: List[str] = []
        self.vars_addr: List[int] = []
        self.call_chain: List[str] = []


class Emitter:
    def emit(self, context: Context) -> List[Instrument]:
        raise NotImplementedError()


class Expression(Emitter):
    def __init__(self, emitter: Emitter) -> None:
        self.emitter = emitter

    def emit(self, context: Context) -> List[Instrument]:
        return self.emitter.emit(context)


class DoBlock(Emitter):
    def __init__(self, exprs: List[Emitter]) -> None:
        self.exprs = exprs

    def emit(self, context: Context) -> List[Instrument]:
        insts = []
        for expr in self.exprs:
            insts.extend(expr.emit(context))
        return insts


class IfBlock(Emitter):
    def __init__(self, cond: Expression, tb: Expression, fb: Expression) -> None:
        self.cond = cond
        self.tb = tb
        self.fb = fb

    def emit(self, context: Context) -> List[Instrument]:
        sid = context  # id
        eid = context  # id
        insts = []
        insts.extend(self.cond.emit(context))
        insts.append(Instrument(Instrument.JZ, sid))
        insts.extend(self.tb.emit(context))
        insts.append(Instrument(Instrument.JMP, eid))
        insts.append(Instrument(Instrument.LAB, sid))
        insts.extend(self.fb.emit(context))
        insts.append(Instrument(Instrument.LAB, eid))
        return insts


class Assignment(Emitter):
    def __init__(self, name: str, expr: Expression) -> None:
        self.var_name = name
        self.expr = expr

    def emit(self, context: Context) -> List[Instrument]:
        vid = context  # id
        insts = []
        insts.extend(self.expr.emit(context))
        insts.append(Instrument(Instrument.CPT, vid))
        context  # add var and bind addr
        return insts


class Function(Emitter):
    def __init__(self, name: str, params: List[str], expr: Expression) -> None:
        self.name = name
        self.params = params
        self.expr = expr

    def emit(self, context: Context) -> List[Instrument]:
        insts = self.expr.emit(context)
        return insts


class Call(Emitter):
    def __init__(self, name: str, args: List) -> None:
        self.func_name = name
        self.args = args

    def emit(self, context: Context) -> List[Instrument]:
        if self.func_name in context.call_chain:
            raise RecursionError(self.func_name)

        insts = []
        vars_addr = []
        vars = []
        for a in self.args:
            if a is Emitter:
                va = context.vars_addr  # TODO
                insts.extend(a.emit(context))
                vars_addr.append(va)
                vars.append(None)
                insts.append(Instrument(Instrument.CPT, va))
            elif a["type"] == "NAME":
                va = context.vars_addr  # TODO
                vars_addr.append(va)
                vars.append(a["value"])
            else:  # a["type"] == "CONST"
                vars_addr.append(0)
                vars.append(int(a["value"]))
        context.vars_addr.append(vars_addr)
        context.vars.append(vars)
        context.call_chain.append(self.func_name)

        if self.func_name in context.builtin_funcs.keys():
            insts = context.builtin_funcs[self.func_name].emit(context)
        else:
            insts = context.funcs[self.func_name].emit(context)

        context.call_chain.pop()
        context.vars.pop()
        context.vars_addr.pop()
        return insts


class Builtin(Emitter):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def emit(self, context: Context) -> List[Instrument]:
        return []


class Read(Builtin):
    def __init__(self) -> None:
        super().__init__("read")

    def emit(self, context: Context) -> List[Instrument]:
        return [Instrument(Instrument.IN)]


class Write(Builtin):
    def __init__(self) -> None:
        super().__init__("write")

    def emit(self, context: Context) -> List[Instrument]:
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 1:
            raise ValueError("'write' accepts 1 arg")
        return [
            Instrument(Instrument.CPF, vars_addr[0]),
            Instrument(Instrument.OUT)
        ]


class Add(Builtin):
    def __init__(self) -> None:
        super().__init__("write")

    def emit(self, context: Context) -> List[Instrument]:
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 2:
            raise ValueError("'add' accepts 2 args")
        # if NAME CONST
        return [
            Instrument(Instrument.CPF, vars_addr[0]),
            Instrument(Instrument.ADD, vars_addr[1])
        ]


class Gt(Builtin):
    def __init__(self) -> None:
        super().__init__("gt")

    def emit(self, context: Context) -> List[Instrument]:
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 2:
            raise ValueError("'gt' accepts 2 args")
        # if NAME CONST
        return [
            Instrument(Instrument.SUB, vars_addr[0]),
            Instrument(Instrument.CPF, vars_addr[0]),
            Instrument(Instrument.ADD, vars_addr[1])
        ]
