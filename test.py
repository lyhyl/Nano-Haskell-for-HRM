from typing import List
from compiler import Add, Call, Compare, Context, Instrument, Read, Sub, Write, header
from optimizer import optimize
from yacc import parser

tests = [
    # """main = do {
    # write read;
    # main
    # }""",
    # """main = do {
    # a <- add read 1;
    # b <- sub 1 read;
    # if gt a b
    #     then write a
    #     else write b;
    # main
    # }""",
    # """main = do {
    # x <- read;
    # y <- read;
    # if lt x 0
    #     then if lt y 0
    #         then write 4
    #         else write 5
    #     else if lt y 0
    #         then write 5
    #         else write 4;
    # main
    # }
    # """,
    """main = do {
    x <- read;
    if gt x 0
        then print_dn x
        else print_up x;
    main
    }
print_dn x
    | eq x 0 = write x
    | gt x 0 = do {
        write x;
        print_dn (sub x 1)
        }
print_up x
    | eq x 0 = write x
    | lt x 0 = do {
        write x;
        print_up (add x 1)
        }"""
]

def print_code(insts: List[Instrument]) -> None:
    insts = '\n'.join(str(i) for i in insts)
    print(f"{header}\n{insts}")

if __name__ == "__main__":
    for test in tests:
        print(test)
        funcs = parser.parse(test)

        entry = Call("main", [])
        context = Context(
            [
                Write(),
                Add(), Sub(),
                Compare("gt", False, True, False),
                Compare("ge", True, True, False),
                Compare("lt", False, True, True),
                Compare("le", True, True, True),
                Compare("eq", True, False, False, False),
                Compare("neq", True, False, False, True)
            ],
            [Read()],
            funcs
        )
        try:
            hrm = entry.emit(context)
            print_code(hrm)
            opt = True
            while opt:
                opt, hrm = optimize(hrm)
            print_code(hrm)

        except Exception as e:
            print(e)
