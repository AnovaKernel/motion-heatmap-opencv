import threading
import tkinter as tk
import tkinter.filedialog
from datetime import datetime
from enum import Enum
from pathlib import Path
from tkinter.scrolledtext import ScrolledText


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.state = State()
        self.grid = {
            Buttons: (0, 0),
            Inputs : (0, 2),
            Preview: (0, 1),
            Flavour: (1, 0),
            Output : (2, 0),
            }
        self.output = None
        self.label = {}
        self.entry = {}
        self.heatmap = None
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def create_widgets(self):
        for group, (x, y) in (self.grid.items()):
            _f = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
            span = 3 if x > 0 else 1
            _f.grid(row=x, column=y, sticky='nwes', columnspan=span)
            for i, widget_type in enumerate(group):
                _line = tk.Frame(master=_f)
                self._add_widgets_to_row(widget_type, master=_line)
                _line.grid(row=i, column=0, sticky='nsew')

    def _add_widgets_to_row(self, type, master=None, ):

        if isinstance(type, Buttons):
            tk.Button(
                master=master,
                text=type.value,
                command=self.get_command(type),
                width=20
                ).pack(side=tk.LEFT)
            _label = tk.Label(master)
            _label.pack(anchor="w")

            # Register this label so we can access it to display info
            self.label[type] = _label

        elif isinstance(type, Inputs):
            tk.Label(master, text=type.value).pack(anchor="e", side=tk.LEFT)
            _widget = tk.Entry(master=master, validate="key", validatecommand=(self.register(is_digit), '%S'), width=10)
            _widget.pack(side=tk.RIGHT)

            # Register this entry so we can read it's value later
            self.entry[type] = _widget

        elif isinstance(type, Output):
            self.output = ScrolledText(master=master, height=8, wrap=tk.WORD)
            self.output.pack(side=tk.BOTTOM,fill=tk.BOTH, expand=True)

        elif isinstance(type, Flavour):
            _label = tk.Label(master=master, text=type.value)
            _label.pack(side=tk.TOP, anchor='w')
            self.label[type] = _label

        elif isinstance(type, Preview):
            # todo:
            tk.Canvas(master=master, bg='black').pack()

        else:
            print(f"{type} not implemented")

    def get_command(self, event):
        if event == Buttons.OPEN_FILE:
            return self.select_file
        elif event == Buttons.EXIT:
            return self.master.destroy
        elif event == Buttons.CREATE_HEATMAP:
            return self.generate_heatmap
        elif event == Buttons.SELECT_REF_FRAME:
            return self.select_ref_frame
        else:
            return lambda: self.add_output(f"{event} not implemented")

    def generate_heatmap(self):
        if self.heatmap:
            self.heatmap.update_settings(self.get_settings())
            # self.parse_entries()

            threading.Thread(target=self.heatmap.read_frames).start()

            threading.Thread(target=self.heatmap.write_frames).start()

        else:
            self.add_output("Can't generate, no input file loaded.")

    def select_file(self):
        file = tk.filedialog.askopenfile(mode="r")
        if file:
            path = file.name
            name = Path(path).name
            self.init_heatmap(path)
            self.add_output(f'Loaded {name} ({self.heatmap.length} frames)')

            self.heatmap.set_reference_frame()
            height, width, _ = self.heatmap.ref_frame.shape
            length = self.heatmap.length
            self.label[Buttons.OPEN_FILE]['text'] = f"File: {name}, Frames: {length}, Dim: {width}x{height}"
            self.label[Buttons.SELECT_REF_FRAME]['text'] = ""
        else:
            self.add_output(f'No file selected')

    def select_ref_frame(self):
        if not self.heatmap:
            self.add_output("Open file first")
            return

        file = tk.filedialog.askopenfile(mode="r")
        if file:
            path = file.name
            name = Path(path).name

            self.heatmap.set_reference_frame(file=path)
            height, width, _ = self.heatmap.ref_frame.shape

            self.label[Buttons.SELECT_REF_FRAME]['text'] = f"File: {name}, Dim: {width}x{height}"
        else:
            self.add_output(f'No file selected')

    def log(self, text, status_only=False):
        if not status_only:
            self.add_output(text)
        else:
            self.set_flavour(text)

    def set_flavour(self, text):
        _label = self.label[Flavour.FLAVOUR_TEXT]
        if _label:
            _label["text"] = text
            _label.update()

    def add_output(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.output.insert(tk.INSERT, f'[{now}] {text} \n')
        self.output.see(tk.END)
        self.output.update()

    def init_heatmap(self, path):
        from motion_heatmap import HeatMapProcessor
        self.heatmap = HeatMapProcessor(input_file=path, logger=self.log, settings=self.get_settings())

    def get_settings(self):
        settings = {}
        for i in Inputs:
            settings[i] = self.entry[i].get()
        return settings


class Buttons(Enum):
    OPEN_FILE = "Open File"
    CREATE_HEATMAP = "Generate Heatmap"
    SELECT_REF_FRAME = "Choose Reference Image"
    PREVIEW = "Preview"
    EXIT = "Exit"


class Inputs(Enum):
    HEAT_INTENSITY = "Heat Intensity"
    THRESHOLD = "Threshold"
    FRAME_SKIP = "Frameskip"
    MAX_FRAMES = "Max Frames"
    OUTPUT_FPS = "Output FPS"


class Preview(Enum):
    PREVIEW = "Preview"


class Output(Enum):
    OUTPUT_LOG = "Output Log"


class Flavour(Enum):
    FLAVOUR_TEXT = "..."


def is_digit(s: str) -> bool:
    return s.isdigit()


class State:
    def __init__(self):
        self.hmp = None

    def dispatch(self, event, *args):
        pass