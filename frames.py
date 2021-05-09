import threading
import tkinter as tk
import tkinter.filedialog
from abc import abstractmethod
from pathlib import Path
from tkinter.scrolledtext import ScrolledText

from heatmap_generator import generate_heatmap, load_file, set_reference_frame
from util import Buttons, Inputs, is_digit


class LayoutFrame(tk.Frame):
    def __init__(self, x, y, span=1, master=None):
        super().__init__(master)
        # self.master = master
        self.root = master
        _f = tk.Frame(master, relief=tk.RAISED, borderwidth=1)
        self.add_widgets(_f)
        _f.grid(row=y, column=x, sticky='nwes', columnspan=span)

    @abstractmethod
    def add_widgets(self, _):
        pass


class ButtonFrame(LayoutFrame):

    def __init__(self, **kwargs):
        super().__init__(0, 0, 1, **kwargs)

    def add_widgets(self, master):
        for i, button in enumerate(Buttons):
            self.add_widget(master, button, i)

    def add_widget(self, master, button, row=0):
        _line = tk.Frame(master=master)
        tk.Button(
            master=_line,
            text=button.value,
            command=self.get_command(button),
            width=20
            ).pack(side=tk.LEFT)
        _label = tk.Label(_line)
        _label.pack(anchor="w")
        _line.grid(row=row, column=0, sticky='nsew')

        # Register this label so we can access it to display info
        self.master.label[button] = _label

    def get_command(self, event):
        if event == Buttons.OPEN_FILE:
            return self.select_file
        elif event == Buttons.EXIT:
            return self.root.master.destroy
        elif event == Buttons.SELECT_REF_FRAME:
            return self.select_ref_frame
        elif event == Buttons.CREATE_HEATMAP:
            return self.generate_heatmap
        else:
            return lambda: self.master.add_output(f"{event} not implemented")

    def select_file(self):
        file = tk.filedialog.askopenfile(mode="r")
        if file:
            self.master.add_output(f"Loading {file}")
            threading.Thread(target=load_file, args=[file.name]).start()
        else:
            self.master.add_output(f"Nothing selected.")

    def generate_heatmap(self):
        self.master.add_output(f"Started Generating")
        threading.Thread(target=generate_heatmap, args=[self.master.get_settings()]).start()

    def select_ref_frame(self):
        file = tk.filedialog.askopenfile(mode="r")
        if file:
            # threading.Thread(target=generate_heatmap, args=[self.master.get_settings()]).start()
            path = file.name
            name = Path(path).name

            height, width = set_reference_frame(file=path)
            # height, width, _ = self.heatmap.ref_frame.shape

            self.master.label[Buttons.SELECT_REF_FRAME]['text'] = f"{name}, {width}x{height}"
        else:
            self.master.add_output(f"Nothing selected.")


class SettingFrame(LayoutFrame):

    def add_widgets(self, master):
        for i, input in enumerate(Inputs):
            self.add_widget(master, input, i)

    def __init__(self, **kwargs):
        super().__init__(1, 0, 1, **kwargs)

    def add_widget(self, master, input, row=0):
        _line = tk.Frame(master=master)
        tk.Label(_line, text=input.value).pack(anchor="e", side=tk.LEFT)
        _widget = tk.Entry(master=_line, validate="key", validatecommand=(self.register(is_digit), '%S'), width=10)
        _widget.pack(side=tk.RIGHT)
        _line.grid(row=row, column=0, sticky='nsew')
        # Register this entry so we can read it's value later
        self.master.entry[input] = _widget


class MessageFrame(LayoutFrame):
    def __init__(self, **kwargs):
        super().__init__(0, 1, 3, **kwargs)

    def add_widgets(self, master):
        self.output = ScrolledText(master=master, height=8, wrap=tk.WORD)
        self.output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.flavour = tk.Label(master=master, text='..')
        self.flavour.pack(side=tk.TOP, anchor='w')


class PreviewFrame(LayoutFrame):
    def __init__(self, **kwargs):
        super().__init__(2, 0, 1, **kwargs)

    def add_widgets(self, master):
        tk.Canvas(master=master, bg='black').pack()