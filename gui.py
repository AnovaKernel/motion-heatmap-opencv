import threading
import time
import tkinter as tk
import tkinter.filedialog
from datetime import datetime
from pathlib import Path
from tkinter.scrolledtext import ScrolledText

from motion_heatmap import HeatMapProcessor
from util import *


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.buttons = [OPEN_FILE, CREATE_HEATMAP, EXIT]
        self.entries = [HEAT_INTENSITY, FRAME_SKIP, MAX_FRAMES]

        self.label = {}
        self.entry = {}
        self.heatmap = None
        self.create_widgets()
        self.pack()

    def create_widgets(self):
        frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        frame.grid(row=0, column=0, sticky='nwes')

        for i, button in enumerate(self.buttons):
            row = tk.Frame(master=frame)
            b = tk.Button(master=row, text=button, command=self.get_command(button), width=20)
            b.pack(side=tk.LEFT)
            lb = tk.Label(master=row)
            lb.pack()
            self.label[button] = lb
            row.grid(row=i, column=0, sticky='ew')

        frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        frame.grid(row=2, column=0, columnspan=2, sticky='n')
        self.status = tk.Label(master=frame, text=f"...")
        self.status.pack(side=tk.TOP, )
        self.output_text = ScrolledText(master=frame, height=5, wrap=tk.WORD)
        self.output_text.pack(side=tk.BOTTOM)

        frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        frame.grid(row=0, column=1, sticky='nwes')
        for i, entry in enumerate(self.entries):
            row = tk.Frame(master=frame)
            lb = tk.Label(master=row, text=entry, width=15, )
            lb.pack(side=tk.LEFT, anchor="w")
            e = tk.Entry(master=row, width=20)
            e.pack()
            self.entry[entry] = e
            row.grid(row=i, column=0, sticky='ew')

    def get_command(self, event):
        if event == OPEN_FILE:
            return self.select_file
        elif event == EXIT:
            return self.master.destroy
        elif event == CREATE_HEATMAP:
            return self.generate_heatmap
        else:
            return lambda: self.log(f"{event} not implemented")

    # def generate_map_image(self):
    #     if self.heatmap:
    #         # todo: threading.Thread(target=self.heatmap.make_image)
    #         self.heatmap.write_image()
    #         self.log('img generation done')
    #     else:
    #         self.log("Can't generate, no input file loaded.")

    def generate_heatmap(self):
        if self.heatmap:
            self.parse_entries()

            threading.Thread(target=self.heatmap.read_frames, daemon=True).start()

            time.sleep(2)

            threading.Thread(target=self.heatmap.write_frames, daemon=True).start()

        else:
            self.log("Can't generate, no input file loaded.")

    def select_file(self):
        file = tk.filedialog.askopenfile(mode="r")
        if file:
            path = file.name
            name = Path(path).name
            self.heatmap = HeatMapProcessor(input_file=path, entries=self.entry, logger=self.log)
            height, width, _ = self.heatmap.ref_frame.shape
            length = self.heatmap.length
            self.label[OPEN_FILE]['text'] = f"File: {name}, Frames: {length}, Dim: {width}x{height}"
            self.log(f'Loaded {name} ({self.heatmap.length} frames)')
        else:
            self.log(f'No file selected')

    def parse_entries(self):
        if self.heatmap:
            max_val = self.entry[HEAT_INTENSITY].get()
            if max_val.isnumeric():
                self.heatmap.max_value = int(max_val)
            step_size = self.entry[FRAME_SKIP].get()
            if step_size.isnumeric():
                self.heatmap.step_size = int(step_size) + 1
            max_frames = self.entry[MAX_FRAMES].get()
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


if __name__ == '__main__':

    root = tk.Tk()
    app = Application(master=root)

    app.mainloop()