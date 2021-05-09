from enum import Enum


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