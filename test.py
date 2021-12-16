tests = [
    """main = do {
    write read
    main
    }""",
    """main = do {
    a <- read
    b <- read
    if a > b
        then write a
        else write b
    }"""
]

if __name__ == "__main__":
    from lex import lexer
    for test in tests:
        lexer.input(test)
        t = lexer.token()
        while t:
            print(t)
            t = lexer.token()
        print("END")

    # from yacc import parser
