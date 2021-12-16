# nano-Haskell for HRM

## Example
question 1-1
```
main = do {
    write read
    main
    }
```
question ?-?
```
main = do {
    a <- read
    b <- read
    if a > b
        then write a
        else write b
    }
```

## BNF grammer
```
PROG = FUNC PROG | empty
FUNC = NAME "=" EXP
EXP = "do" "{" STMTS "}" | "if" COMP "then" EXP ["else" EXP] | FEXP | COMP
STMTS = STMT STMTS | EXP
STMT = ASSIGN | EXP
FEXP = NAME "(" AEXP ")"
AEXP = NAME AEXP | empty
ASSIGN = NAME "<-" EXPR
COMP = MATH ">" COMP | MATH "<" COMP | MATH
MATH = MATH "+" TERM | MATH "-" TERM | TERM
TERM = TERM "*" FACTOR | FACTOR
FACTOR = "(" MATH ")" | FEXP | NAME | CONST
NAME = r"[_A-Za-z]+[_0-9A-Za-z]*"
CONST = r"\d+"
```

The default entrance point is `main` function.

## recursion & tail recursion

CPS transform
