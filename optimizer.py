from typing import List, Tuple
from bisect import bisect_right
from compiler import Instrument


def optimize(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    os = [
        o_redundant_copy,
        o_continuous_label,
        o_immediate_jump,
        o_unref_label,
        o_dead_code,
        remap_labels
    ]
    optimized = False
    for f in os:
        r, hrm = f(hrm)
        optimized = optimized or r
    return optimized, hrm


def o_redundant_copy(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    opt = []
    i = 0
    while i < len(hrm):
        opt.append(hrm[i])
        if hrm[i].code.startswith("COPY"):
            j = i + 1
            while j < len(hrm) and hrm[j].code.startswith("COPY") and hrm[j].arg == hrm[i].arg:
                j += 1
            i = j
        else:
            i += 1
    return len(opt) < len(hrm), opt


def o_unref_label(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    labs = set(i.arg for i in hrm if i.code == Instrument.LAB)
    jmps = set(i.arg for i in hrm if i.code.startswith("JUMP"))
    unrefs = labs.difference(jmps)
    opt = [i for i in hrm if i.code != Instrument.LAB or i.arg not in unrefs]
    return len(unrefs) > 0, opt


def o_continuous_label(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    glabs = []
    i = 0
    while i < len(hrm):
        g = []
        while hrm[i].code == Instrument.LAB:
            g.append(hrm[i].arg)
            i += 1
        if len(g) > 1:
            glabs.append(g)
        i += 1
    opt = hrm.copy()
    for g in glabs:
        if len(g) > 1:
            t = g[0]
            opt = [
                (Instrument(ins.code, t) if (ins.code.startswith("JUMP") and ins.arg in g[1:]) else ins)
                for ins in opt]
    return len(glabs) > 0, opt


def o_dead_code(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    ijmp = [i for i in range(len(hrm)) if hrm[i].code == Instrument.JMP]
    ilab = [i for i in range(len(hrm)) if hrm[i].code == Instrument.LAB]

    if len(ijmp) == 0:
        return False, hrm

    ilab.append(len(hrm))
    secs = [(j + 1, ilab[bisect_right(ilab, j)]) for j in ijmp]
    secs = [(i, j) for i, j in secs if j - i > 0]
    secs.reverse()
    opt = hrm.copy()
    for l, r in secs:
        for _ in range(r - l):
            opt.pop(l)

    return len(secs) > 0, opt


def o_immediate_jump(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    ij = [(hrm[i].arg, hrm[i + 1].arg) for i in range(len(hrm) - 1)
          if hrm[i].code == Instrument.LAB and hrm[i + 1].code == Instrument.JMP]
    opt = hrm.copy()
    for i, j in ij:
        opt = [Instrument(ins.code, j) if (ins.code.startswith("JUMP") and ins.arg == i) else ins
               for ins in hrm]
    return len(ij) > 0, opt


def remap_labels(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    lab = [i.arg for i in hrm if i.code == Instrument.LAB]
    lab = sorted(set(lab))
    if lab == list(range(len(lab))):
        return False, hrm
    else:
        opt = []
        for i in hrm:
            if i.code == Instrument.LAB or i.code.startswith("JUMP"):
                idx = lab.index(i.arg)
                opt.append(Instrument(i.code, idx))
            else:
                opt.append(i)
        return True, opt
