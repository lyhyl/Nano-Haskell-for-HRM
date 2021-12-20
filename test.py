from typing import List
from compiler import Add, Addr, Call, Compare, Context, Instrument, Nop, Read, Sub, Write, header
from optimizer import optimize
from yacc import parser

tests = [
    # """main = do {
    # write read;
    # main
    # }""",
    # """main = do {
    # a <- read;
    # b <- read;
    # if gt a b
    #     then write a
    #     else write b;
    # main
    # }"""
    # """main = do {
    # x <- read;
    # y <- read;
    # if lt x 0
    #     then if lt y 0
    #         then write (addr 4)
    #         else write (addr 5)
    #     else if gt y 0
    #         then write (addr 4)
    #         else write (addr 5);
    # main
    # }""",
#     """main = do {
#     x <- read;
#     if gt x 0
#         then print_dn x
#         else print_up x;
#     main
#     }
# print_dn x
#     | eq x 0 = write x
#     | gt x 0 = do {
#         write x;
#         print_dn (sub x 1)
#         }
# print_up x
#     | eq x 0 = write x
#     | lt x 0 = do {
#         write x;
#         print_up (add x 1)
#         }""",
#     """main = do {
#     x <- read;
#     if gt x 0
#         then print_dn x
#         else print_up x;
#     main
#     }
# print_dn x = if eq x 0
#     then write x
#     else do {
#         write x;
#         print_dn (sub x 1)
#         }
# print_up x = if eq x 0
#     then write x
#     else do {
#         write x;
#         print_up (add x 1)
#         }""",
# """main = do {
#     write (mul read read (addr 9));
#     main
# }

# mul a b acc
#     | eq a 0 = addr 9
#     | eq b 0 = addr 9
#     | gt b 0 = mul a (sub b 1) (add acc a)""",
"""main = do {
    fib (addr 9) (add (addr 9) 1) read;
    main
}

fib a b x
    | le b x = do {
        write b;
        fib b (add a b) x
    }""",
# """main = do {
#     write (addr read);
#     main
# }
# """,
# """main = do {
#     pt read;
#     main
# }
# pt x = if neq (addr x) 0
#             then do {
#                 write (addr x);
#                 pt (add x 1)
#             }
#             else nop
# """
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
                Addr(),
                Write(),
                Add(), Sub(),
                Compare("gt", False, True, False),
                Compare("ge", True, True, False),
                Compare("lt", False, True, True, True),
                Compare("le", True, True, True, True),
                Compare("eq", True, False, False, True),
                Compare("neq", True, False, False, False)
            ],
            [Read(), Nop()],
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
