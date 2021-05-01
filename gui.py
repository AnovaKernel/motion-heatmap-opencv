import tkinter as tk
import tkinter.filedialog
from datetime import datetime
from pathlib import Path
from tkinter.scrolledtext import ScrolledText

from motion_heatmap import HeatMapProcessor


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.open_file_button = tk.Button(self, text="Select Video File", command=self.select_file)
        self.open_file_button.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self.create_img = tk.Button(self, text="Generate Heatmap Image", command=self.generate_map_image)
        self.create_img.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self.create_vid = tk.Button(self, text="Generate Heatmap Video", command=self.generate_map_video)
        self.create_vid.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self.quit = tk.Button(self, text="Exit", command=self.master.destroy)
        self.quit.pack()

        self.output_text = ScrolledText(height=5, wrap=tk.WORD)
        self.output_text.pack()

    def generate_map_image(self):
        self.log('starting img generation')
        # todo: threading.Thread(target=self.heatmap.make_image)
        self.heatmap.make_image()
        self.log('img generation done')

    def generate_map_video(self):
        self.log('starting vid generation')
        # todo: threading.Thread(target=self.heatmap.make_video)
        self.heatmap.make_video()
        self.log('vid generation done')

    def select_file(self):
        file = tk.filedialog.askopenfile(mode="r")
        path = file.name
        name = Path(path).name
        self.heatmap = HeatMapProcessor(input_file=path, logger=self.log)
        self.log(f'Loaded {name} ({self.heatmap.length} frames)')
        self.open_file_button['text'] = name

    def log(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.INSERT, f'[{now}] {text} \n')
        self.output_text.see(tk.END)
        self.output_text.update()


if __name__ == '__main__':

    root = tk.Tk()
    app = Application(master=root)

    app.mainloop()