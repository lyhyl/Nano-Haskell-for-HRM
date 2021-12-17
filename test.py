tests = [
    """main = do {
    write read;
    main
    }""",
    """main = do {
    a <- read;
    b <- read;
    if gt a b
        then write a
        else write b;
    main
    }"""
]

if __name__ == "__main__":
    from yacc import parser
    for test in tests:
        print(test)
        parser.parse(test)
