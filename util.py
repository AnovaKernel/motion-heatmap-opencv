from enum import Enum


class Buttons(Enum):
    OPEN_FILE = "Open File"
    CREATE_HEATMAP = "Generate Heatmap"
    SELECT_REF_FRAME = "Choose Reference Image"
    PREVIEW = "Preview"
    EXIT = "Exit"


class Inputs(Enum):
    HEAT_INTENSITY = "Change Intensity (Default: 2)"
    VARIANCE_THRESHOLD = "Variance Sensitivity (Default: 50)"
    FRAME_SKIP = "Frameskip (Default: 0)"
    MAX_FRAMES = "Stop After Frames (Default: 0)"
    OUTPUT_FPS = "Output FPS (Default: 30)"
    HIST_FRAMES = "Background History Frames (Default: 100)"
    DETECT_SHADOWS = "Detect Shadows (Default: 0)"
    ERODE_ITERATIONS = "Erosion Iterations (Default: 0)"


class Preview(Enum):
    PREVIEW = "Preview"


class Output(Enum):
    OUTPUT_LOG = "Output Log"


class Flavour(Enum):
    FLAVOUR_TEXT = "..."


def is_digit(s: str) -> bool:
    return s.isdigit()