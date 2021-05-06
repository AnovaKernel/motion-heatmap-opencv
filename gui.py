import threading
import tkinter as tk
import tkinter.filedialog
from datetime import datetime
from enum import Enum
from pathlib import Path


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

        self.label = {}
        self.entry = {}
        self.heatmap = None
        self.create_widgets()
        self.pack()

    def create_widgets(self):

        for group, (x, y) in (self.grid.items()):
            f = tk.Frame(self, relief=tk.RAISED, borderwidth=1)

            f.grid(row=x, column=y, sticky='nwes')
            for i, wtype in enumerate(group):
                _line = tk.Frame(master=f)
                _w, _l = self._create_widget(wtype, master=_line)
                _w.pack(side=tk.LEFT)
                _l.pack(anchor="w")

                _line.grid(row=i, column=0, sticky='nsew')
                print(wtype)

        # frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)  # frame.grid(row=0, column=0, sticky='nwes')

        # for i, button in enumerate(Buttons):  #     row = tk.Frame(master=frame)  #     b = tk.Button(master=row, text=button.value, command=self.get_command(button), width=20)  #  #     b.pack(side=tk.LEFT)  #     lb = tk.Label(master=row)  #     lb.pack(anchor="w")

        #     row.grid(row=i, column=0, sticky='ew')

        #  # frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)  # frame.grid(row=2, column=0, columnspan=2, sticky='n')  # self.status = tk.Label(master=frame, text=f"...")  # self.status.pack(side=tk.TOP, )  # self.output_text = ScrolledText(master=frame, height=7, wrap=tk.WORD)  # self.output_text.pack(side=tk.BOTTOM)  # self.bell()  #  # frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)  # frame.grid(row=0, column=1, sticky='nwes')  # for i, entry in enumerate(Inputs):  #     row = tk.Frame(master=frame)  #     lb = tk.Label(master=row, text=entry.value, width=15, )  #     lb.pack(side=tk.LEFT, anchor="w")  #     vcmd = self.register(is_digit), '%S'  #     e = tk.Entry(master=row, width=20, validate="key", validatecommand=vcmd)  #     e.pack()  #  #     self.entry[entry] = e  #     row.grid(row=i, column=0, sticky='ew')  #

    def _create_widget(self, type, master=None, ):
        label = tk.Label(master)
        if isinstance(type, Buttons):
            widget = tk.Button(master=master, text=type.value, command=self.get_command(type), width=20)
        elif isinstance(type, Inputs):
            widget = tk.Entry(master)
        return widget, label

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
            return lambda: self.log(f"{event} not implemented")

    def generate_heatmap(self):
        if self.heatmap:
            self.parse_entries()

            threading.Thread(target=self.heatmap.read_frames, daemon=True).start()

            threading.Thread(target=self.heatmap.write_frames, daemon=True).start()

        else:
            self.log("Can't generate, no input file loaded.")

    def select_file(self):
        file = tk.filedialog.askopenfile(mode="r")
        if file:
            path = file.name
            name = Path(path).name
            self.init_heatmap(path)
            self.log(f'Loaded {name} ({self.heatmap.length} frames)')

            self.heatmap.set_reference_frame()
            height, width, _ = self.heatmap.ref_frame.shape
            length = self.heatmap.length
            self.label[Buttons.OPEN_FILE]['text'] = f"File: {name}, Frames: {length}, Dim: {width}x{height}"
            self.label[Buttons.SELECT_REF_FRAME]['text'] = ""
        else:
            self.log(f'No file selected')

    def select_ref_frame(self):
        if not self.heatmap:
            self.log("Open file first")
            return

        file = tk.filedialog.askopenfile(mode="r")
        if file:
            path = file.name
            name = Path(path).name

            self.heatmap.set_reference_frame(file=path)
            height, width, _ = self.heatmap.ref_frame.shape

            self.label[Buttons.SELECT_REF_FRAME]['text'] = f"File: {name}, Dim: {width}x{height}"
        else:
            self.log(f'No file selected')

    def parse_entries(self):
        if self.heatmap:
            max_val = self.entry[Buttons.HEAT_INTENSITY].get()
            if max_val.isnumeric():
                self.heatmap.max_value = int(max_val)
            step_size = self.entry[Buttons.FRAME_SKIP].get()
            if step_size.isnumeric():
                self.heatmap.step_size = int(step_size) + 1
            max_frames = self.entry[Buttons.MAX_FRAMES].get()
            if max_frames.isnumeric():
                self.heatmap.max_frames = int(max_frames)

    def log(self, text, status_only=False):
        if not status_only:
            now = datetime.now().strftime("%H:%M:%S")
            self.output_text.insert(tk.INSERT, f'[{now}] {text} \n')
            self.output_text.see(tk.END)
            self.output_text.update()
        else:
            self.status["text"] = text
            self.status.update()

    def init_heatmap(self, path):
        from motion_heatmap import HeatMapProcessor
        self.heatmap = HeatMapProcessor(input_file=path, entries=self.entry, logger=self.log)


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
    pass


class Output(Enum):
    pass


class Flavour(Enum):
    pass


def is_digit(s: str):
    return s.isdigit()


class State:
    def __init__(self):
        self.hmp = None

    def dispatch(self, event, *args):
        pass