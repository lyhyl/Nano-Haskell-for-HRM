# nano-Haskell for HRM

## Example
puzzle 2
```
main = do {
    write read;
    main
    }
```

puzzle 14
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

puzzle 19
```
main = do {
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
        }
```

puzzle 20
```
main = do {
    write (mul read read (addr 9));
    main
}

mul a b acc
    | eq a 0 = addr 9
    | eq b 0 = addr 9
    | eq b 1 = add acc a
    | gt b 1 = mul a (sub b 1) (add acc a)
```

puzzle 22
```
main = do {
    fib (addr 9) (add (addr 9) 1) read;
    main
}

fib a b x
    | le b x = do {
        write b;
        fib b (add a b) x
    }
    | gt b x = nop
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
- `eq` equal
- `neq` not equal
- `gt` greater
- `lt` less
- `ge` greater or equal
- `le` less or equal
- `add` addition
- `sub` subtraction

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
