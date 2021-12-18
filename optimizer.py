from typing import List, Tuple
from compiler import Instrument


def optimize(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    os = [
        o_unref_label,
        o_redundant_copy,
        remap_labels
    ]
    optimized = False
    for opt in os:
        r, hrm = opt(hrm)
        optimized = optimized or r
    return optimized, hrm


def o_redundant_copy(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    opt = []
    i = 0
    while i < len(hrm):
        opt.append(hrm[i])
        if hrm[i].code == Instrument.CPT:
            j = i + 1
            while j < len(hrm) and\
                (hrm[j].code == Instrument.CPT or hrm[j].code == Instrument.CPF) and\
                    hrm[j].arg == hrm[i].arg:
                j += 1
            i = j
        else:
            i += 1
    return len(opt) < len(hrm), opt


def o_unref_label(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    labs = set(i.arg for i in hrm if i.code == Instrument.LAB)
    jmps = set(i.arg for i in hrm if i.code.startswith("JUMP"))
    unrefs = labs.difference(jmps)
    hrm = [i for i in hrm if i.code != Instrument.LAB or i.arg not in unrefs]
    return len(unrefs) > 0, hrm


def remap_labels(hrm: List[Instrument]) -> Tuple[bool, List[Instrument]]:
    return False, hrm
