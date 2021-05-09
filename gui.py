import threading
import tkinter as tk
import tkinter.filedialog
from datetime import datetime
from pathlib import Path

from frames import ButtonFrame, MessageFrame, PreviewFrame, SettingFrame
from heatmap_generator import HeatMapProcessor
from util import Buttons, Inputs


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        # keep track of labels for easy updating
        self.label = {}
        self.entry = {}

        # initialize the layout frames
        self.top_left = ButtonFrame(master=self)
        self.top_mid = SettingFrame(master=self)
        self.top_right = PreviewFrame(master=self)
        self.bottom = MessageFrame(master=self)

        self._hmp = HeatMapProcessor.get_instance()
        self._hmp.set_output_logger(self.add_output, self.set_flavour)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.pack(fill=tk.BOTH, expand=True)






    def set_flavour(self, text):
        _label = self.bottom.flavour
        _label["text"] = text
        _label.update()

    def add_output(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        _output = self.bottom.output
        _output.insert(tk.INSERT, f'[{now}] {text} \n')
        _output.see(tk.END)
        _output.update()


    def get_settings(self):
        settings = {}
        for i in Inputs:
            settings[i] = self.entry[i].get()
        return settings