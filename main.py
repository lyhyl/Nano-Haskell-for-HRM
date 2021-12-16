from tkinter import Widget

from yacc import parser


def main():
    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        result = parser.parse(s)
        print(result)


if __name__ == "__main__":
    main()
