from typing import List, Tuple, Union

header = "-- HUMAN RESOURCE MACHINE PROGRAM --"
indirect = 64


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
            return f"{chr(self.arg + ord('a'))}:"
        elif self.code in [Instrument.IN, Instrument.OUT]:
            return f"{pad}{self.code}"
        elif self.code.startswith("COPY"):
            addr = str(self.arg) if self.arg < indirect else f"[{self.arg - indirect}]"
            return f"{pad}{self.code:9s}{addr}"
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
        self.vars_val: List[List[int]] = []
        self.vars_addr: List[List[int]] = []
        self.vars_name: List[List[str]] = [[]]
        self.call_chain: List[str] = []
        self.call_label: List[int] = []
        self.jz = False
        self.jn = False
        self.swap_branch = False
        self.label_count = 0
        self.pending_addr_offset = 0

    def get_next_label(self) -> int:
        label = self.label_count
        self.label_count += 1
        return label

    def get_var_addr(self) -> int:
        if len(self.vars_addr) == 0 or len(self.vars_addr[-1]) == 0:
            return 0
        return abs(self.vars_addr[-1][-1]) + 1 + self.pending_addr_offset

    def name_lookup(self, name: str) -> List[Instrument]:
        names = self.vars_name[-1]
        if name in names:
            va = self.vars_addr[-1][names.index(name)]
            return [Instrument(Instrument.CPF, va)]
        elif name in self.builtin_actns.keys():
            return self.builtin_actns[name].emit(self)
        else:
            raise ValueError(f"name {name} not found")
    
    def func_lookup(self, name: str) -> List[Instrument]:
        if name in self.builtin_funcs.keys():
            return self.builtin_funcs[name].emit(self)
        elif name in self.funcs.keys():
            return self.funcs[name].emit(self)
        else:
            raise ValueError(f"func {name} not found")

    def get_jmp_instruments(self, lab: int) -> List[Instrument]:
        if self.jz and self.jn:
            js = [Instrument.JZ, Instrument.JN]
        elif self.jz or self.jn:
            js = [Instrument.JZ if self.jz else Instrument.JN]
        else:
            js = [Instrument.JZ, Instrument.JN]
        self.jz = False
        self.jn = False
        return [Instrument(j, lab) for j in js]


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
        slab = context.get_next_label()
        elab = context.get_next_label()
        insts = []

        insts.extend(self.cond.emit(context))
        b0, b1 = self.tb, self.fb
        if context.swap_branch:
            b0, b1 = b1, b0
        insts.extend(context.get_jmp_instruments(slab))
        insts.extend(b0.emit(context))
        insts.append(Instrument(Instrument.JMP, elab))
        insts.append(Instrument(Instrument.LAB, slab))
        insts.extend(b1.emit(context))
        insts.append(Instrument(Instrument.LAB, elab))
        return insts


class Assignment(Emitter):
    def __init__(self, name: str, expr: Expression) -> None:
        self.var_name = name
        self.expr = expr

    def emit(self, context: Context) -> List[Instrument]:
        insts = []
        insts.extend(self.expr.emit(context))
        va = context.get_var_addr()
        insts.append(Instrument(Instrument.CPT, va))
        context.vars_addr[-1].append(va)
        context.vars_name[-1].append(self.var_name)
        context.vars_val[-1].append(0)
        return insts


class Guards(Emitter):
    def __init__(self, guards: List[Tuple[Expression, Expression]]) -> None:
        self.guards = guards
        self.emitter = self.desugar(self.guards)
    
    def desugar(self, guards: List[Tuple[Expression, Expression]]) -> IfBlock:
        cond, expr = guards[0]
        if len(guards) == 1:
            return IfBlock(cond, expr, Nop())
        else:
            return IfBlock(cond, expr, self.desugar(guards[1:]))

    def emit(self, context: Context) -> List[Instrument]:
        return self.emitter.emit(context)


class Function(Emitter):
    def __init__(self, name: str, params: List[str], body: Union[Expression, Guards]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def emit(self, context: Context) -> List[Instrument]:
        context.vars_name.append(self.params.copy())
        insts = self.body.emit(context)
        context.vars_name.pop()
        return insts


class Call(Emitter):
    def __init__(self, name: str, args: List) -> None:
        self.func_name = name
        self.args = args

    def emit(self, context: Context) -> List[Instrument]:
        if self.func_name in context.call_chain:
            if self.func_name == context.call_chain[-1]:
                if len(context.funcs[self.func_name].params) > 0:
                    insts, va, vv = self.prepare_args(context)
                    tva = context.vars_addr[-1][:len(self.args)]
                    assert len(va) == len(tva)
                    for f, t in zip(va, tva):
                        insts.append(Instrument(Instrument.CPF, f))
                        insts.append(Instrument(Instrument.CPT, t))
                else:
                    insts = []
                insts.append(Instrument(Instrument.JMP, context.call_label[-1]))
                return insts
            else:
                raise RecursionError(self.func_name)

        if self.func_name in context.builtin_actns.keys():
            return context.builtin_actns[self.func_name].emit(context)

        insts, vars_addr, vars_val = self.prepare_args(context)
        context.vars_addr.append(vars_addr)
        context.vars_val.append(vars_val)

        context.call_chain.append(self.func_name)
        call_label = context.get_next_label()
        context.call_label.append(call_label)

        insts.append(Instrument(Instrument.LAB, call_label))
        insts.extend(context.func_lookup(self.func_name))

        context.vars_val.pop()
        context.vars_addr.pop()

        context.call_label.pop()
        context.call_chain.pop()

        return insts

    def prepare_args(self, context: Context):
        base_va = context.get_var_addr()
        local_va = 0
        insts = []
        vars_addr = []
        vars_val = []
        for a in self.args:
            va = base_va + local_va
            local_va += 1
            context.pending_addr_offset = local_va
            if isinstance(a, Emitter):
                insts.extend(a.emit(context))
                insts.append(Instrument(Instrument.CPT, va))
                vars_addr.append(va)
                vars_val.append(None)
            elif a["type"] == "NAME":
                insts.extend(context.name_lookup(a["value"]))
                insts.append(Instrument(Instrument.CPT, va))
                vars_addr.append(va)
                vars_val.append(0)
            else:  # a["type"] == "CONST"
                vars_addr.append(-(va + 1))
                vars_val.append(int(a["value"]))
        context.pending_addr_offset = 0
        return insts, vars_addr, vars_val


class Builtin(Emitter):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def emit(self, context: Context) -> List[Instrument]:
        raise NotImplementedError()


class Nop(Builtin):
    def __init__(self) -> None:
        super().__init__("nop")
    
    def emit(self, context: Context) -> List[Instrument]:
        return []


class Addr(Builtin):
    def __init__(self) -> None:
        super().__init__("addr")

    def emit(self, context: Context) -> List[Instrument]:
        vars_val = context.vars_val[-1]
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 1:
            raise ValueError("'addr' accepts 1 arg")
        # return [Instrument(Instrument.CPF, -vars_val[0])]
        if vars_addr[0] < 0:
            return [Instrument(Instrument.CPF, vars_val[0])]
        else:
            return [Instrument(Instrument.CPF, vars_addr[0] + indirect)]


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
        va = vars_addr[0]
        if va < 0:
            raise ValueError("'write' accepts a var")
        return [
            Instrument(Instrument.CPF, va),
            Instrument(Instrument.OUT)
        ]


class Add(Builtin):
    def __init__(self) -> None:
        super().__init__("add")

    def emit(self, context: Context) -> List[Instrument]:
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 2:
            raise ValueError("'add' accepts 2 args")
        va = context.get_var_addr()
        if any(a < 0 for a in vars_addr):  # has constant
            if all(a < 0 for a in vars_addr):
                raise ValueError(f"invoke '{self.name}' with two constants")
            else:
                v0c = vars_addr[0] < 0
                v = vars_addr[1 if v0c else 0]
                c = context.vars_val[-1][0 if v0c else 1]
                ins = Instrument.INC if c > 0 else Instrument.DEC
                return [
                    Instrument(Instrument.CPF, v),
                    Instrument(Instrument.CPT, va),
                    *([Instrument(ins, va)] * abs(c))
                ]
        else:  # two addr
            return [
                Instrument(Instrument.CPF, vars_addr[0]),
                Instrument(Instrument.CPT, va),
                Instrument(Instrument.CPF, vars_addr[1]),
                Instrument(Instrument.ADD, va)
            ]


class Sub(Builtin):
    def __init__(self) -> None:
        super().__init__("sub")

    def emit(self, context: Context) -> List[Instrument]:
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 2:
            raise ValueError(f"'sub' accepts 2 args")
        va = context.get_var_addr()
        if any(a < 0 for a in vars_addr):  # has constant
            if all(a < 0 for a in vars_addr):
                raise ValueError(f"invoke 'sub' with two constants")
            else:
                v0c = vars_addr[0] < 0
                v = vars_addr[1 if v0c else 0]
                c = context.vars_val[-1][0 if v0c else 1]
                if v0c:  # const - v
                    ins = Instrument.INC if c > 0 else Instrument.DEC
                    return [
                        Instrument(Instrument.CPF, v),
                        Instrument(Instrument.CPT, va),
                        Instrument(Instrument.SUB, va),
                        Instrument(Instrument.SUB, va),
                        Instrument(Instrument.CPT, va),
                        *([Instrument(ins, va)] * abs(c))
                    ]
                else:  # v - const
                    ins = Instrument.DEC if c > 0 else Instrument.INC
                    return [
                        Instrument(Instrument.CPF, v),
                        Instrument(Instrument.CPT, va),
                        *([Instrument(ins, va)] * abs(c))
                    ]
        else:  # two addr
            v0, v1 = vars_addr
            return [
                Instrument(Instrument.CPF, v1),
                Instrument(Instrument.CPT, va),
                Instrument(Instrument.CPF, v0),
                Instrument(Instrument.SUB, va)
            ]


class Compare(Builtin):
    def __init__(self, name: str, jz: bool, jn: bool, swap_var: bool, swap_branch: bool = False) -> None:
        super().__init__(name)
        self.jz = jz
        self.jn = jn
        self.swap_var = swap_var
        self.swap_branch = swap_branch

    def emit(self, context: Context) -> List[Instrument]:
        vars_addr = context.vars_addr[-1]
        if len(vars_addr) != 2:
            raise ValueError(f"'{self.name}' accepts 2 args")
        if all(a < 0 for a in vars_addr):
            raise ValueError(f"invoke '{self.name}' with two constants")

        if self.swap_var:
            # a, b = context.vars_name[-1]
            # context.vars_name[-1] = [a, b]
            a, b = context.vars_addr[-1]
            context.vars_addr[-1] = [a, b]
            a, b = context.vars_val[-1]
            context.vars_val[-1] = [a, b]

        insts = Sub().emit(context)

        if self.swap_var:
            # a, b = context.vars_name[-1]
            # context.vars_name[-1] = [a, b]
            a, b = context.vars_addr[-1]
            context.vars_addr[-1] = [a, b]
            a, b = context.vars_val[-1]
            context.vars_val[-1] = [a, b]

        context.jz = self.jz
        context.jn = self.jn
        context.swap_branch = self.swap_branch

        return insts
