import tkinter as tk

from yacc import parser


def main():
    window = tk.Tk()

    for i in range(2):
        window.columnconfigure(i, weight=1)
        window.rowconfigure(i, weight=1)

        for j in range(0, 2):
            frame = tk.Frame(
                master=window,
                relief=tk.RAISED,
                borderwidth=1
            )
            frame.grid(row=i, column=j, padx=5, pady=5)

            label = tk.Label(master=frame, text=f"Row {i}\nColumn {j}")
            label.pack(padx=5, pady=5)

    window.mainloop()


if __name__ == "__main__":
    main()
