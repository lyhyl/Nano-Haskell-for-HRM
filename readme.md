# nano-Haskell for HRM

## Example
puzzle 2
```
main = do {
    write read;
    main
    }
```

puzzle ?-?
```
main = do {
    a <- read;
    b <- read;
    if gt a b
        then write a
        else write b;
    main
    }
```

## BNF grammar
```
PROG = FUNC PROG | empty
FUNC = NAME PARMS "=" EXPR | NAME PARMS GUARDS
PARMS = NAME PARMS | empty
GUARDS = GUARD GUARDS | GUARD
GUARD = "|" EXPR "=" EXPR
EXPR = "do" "{" STMTS "}" | "if" EXPR "then" EXPR "else" EXPR | CALL (| NAME???)
STMTS = STMT ";" STMTS | EXPR
STMT = ASSG | EXPR
ASSG = NAME "<-" EXPR
CALL = NAME ARGS
ARGS = ARG ARGS | empty
ARG = "(" CALL ")" | NAME | CONST
NAME = r"[a-z][_0-9A-Za-z]*"
CONST = r"-?\d+"
```

## Built-in (prelude) function and entry point
### IO
- `read` read in (action)
- `write` write out (function)
### Arithmetic
- `eq` greater
- `gt` greater
- `lt` less
- `ge` greater or equal
- `le` less or equal
- `add` addition
- `sub` subtraction
- `mul` multiplication

The default entry point is `main` function.

## Recursion
Currently, support **tail self-recursion** only.

## Optimization
- Redundant copy
```
...
    COPYTO x
    COPYFROM x
...
```

- Unref label
```
...
a:
...
```

- Continuous label
```
...
a:
b:
...
```

- Dead code
```
...
    JUMP b
    ...No label inside...
c:
...
```

- Immediate jump
```
...
    JUMP a
...
a:
    JUMP b
...
```
