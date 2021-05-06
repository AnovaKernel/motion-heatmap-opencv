from tkinter import Tk

from gui import Application


def main():
    root = Tk()
    app = Application(master=root)

    app.mainloop()


if __name__ == '__main__':
    main()