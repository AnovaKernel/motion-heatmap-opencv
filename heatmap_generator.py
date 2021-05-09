import copy
import datetime
import os.path
import queue
import threading
import time

import cv2
import numpy as np

from util import Inputs


class HeatMapProcessor(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = HeatMapProcessor()
        return cls._instance

    def __init__(self, settings=None) -> None:
        super().__init__()

        self.capture = None
        self.input_frame_count = None

        self.logger = lambda s: print(s)
        self.video_writer = None
        self.ref_frame = None
        self.frame_queue = queue.Queue()
        self.accumulated_img = None
        # self.get_reference_frame()
        self.read_input_done = False
        self.settings = settings
        self.preview = None

    def set_input_file(self, input_file):
        self.capture = cv2.VideoCapture(input_file)
        self.input_frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.ref_frame = None

    def set_output_logger(self, log_method, flavour_text):
        self.logger = log_method
        self.set_flavour = flavour_text

    def set_reference_frame(self, frame=None, file=None):
        if frame:
            self.ref_frame = copy.deepcopy(frame)
        elif file:
            _, self.ref_frame = copy.deepcopy(cv2.VideoCapture(file).read())
        else:
            _, self.ref_frame = copy.deepcopy(self.capture.read())

        h, w, _ = self.ref_frame.shape
        self.logger(f'Reference Frame Loaded ({w}x{h})')
        return h, w

    def iterate_frames(self):

        start_ms = round(time.time() * 1000)
        start_dt = datetime.datetime.now()

        if self.ref_frame is None:
            self.set_reference_frame()

        self.accumulated_img = np.zeros(self.ref_frame.shape[:2], np.uint8)

        # handles color intensity
        last_frame = min(self.input_frame_count - 1,
                         self.max_frames * self.step_size) if self.max_frames > 0 else self.input_frame_count - 1
        frames_read = 0

        bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=self.bg_history,
                                                           varThreshold=self.var_threshold,
                                                           detectShadows=self.shadows)

        self.logger(f'Processing {int(last_frame / self.step_size)} frames')

        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        for i in range(0, last_frame, self.step_size):
            # account for step_size by setting capture frame position
            if self.step_size > 1:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, i)

            ret, frame = self.capture.read()

            if not ret:
                break

            frames_read += 1

            # remove the background
            background_filter = bg_subtractor.apply(frame, 1)
            # cv2.imshow('bgfil', background_filter)

            if self.erode:
                # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
                background_filter = cv2.erode(background_filter, None, iterations=self.erode)

            if self.shadows:
                # shadows are set to 127
                th = 128
            else:
                th = 2

            # if a pixel value is greater then var_threshold, set it to intensity, otherwise 0
            ret, th1 = cv2.threshold(background_filter, th, self.intensity, cv2.THRESH_BINARY)

            # add to the accumulated image
            self.accumulated_img = cv2.add(self.accumulated_img, th1)

            # apply colormap to grayscale values
            color_image = cv2.applyColorMap(self.accumulated_img, self.color_map)

            # frame*alpha+color_image*beta+gamma
            video_frame = cv2.addWeighted(frame, 0.7, color_image, 0.7, 0)

            self.frame_queue.put(video_frame)

            if (i + self.step_size) % (self.step_size * 10) == 0:
                avg_frame_time = ((round(time.time() * 1000) - start_ms) / frames_read)
                to_go = int(last_frame / self.step_size) - frames_read

                self.set_flavour(f'[{round(i / last_frame * 100)}%] '
                                 f'[{to_go} remaining] '
                                 f'[{int(avg_frame_time)} ms/frame] '
                                 f'ETA: [{round(to_go * avg_frame_time / 1000)} sec.]')
                # todo, preview isnt working yet
                self.preview()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        tt = (datetime.datetime.now() - start_dt)
        logentry = f'Done. {frames_read} frames read in {int(tt.total_seconds())} seconds'
        self.set_flavour(logentry)
        self.logger(logentry)
        # cv2.destroyAllWindows()

    def write_image(self):
        color_image = cv2.applyColorMap(cv2.erode(self.accumulated_img, None, 2), cv2.COLORMAP_HOT)
        result_overlay = cv2.addWeighted(self.ref_frame, 0.7, color_image, 0.7, 0)

        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f'output/{ts}'

        _info = f'_h{self.bg_history}_v{self.var_threshold}_i{self.intensity}_s{self.shadows}_e{self.erode}'
        # save the final heatmap
        cv2.imwrite(f"{output_file}{_info}.jpg", result_overlay)
        cv2.imwrite(f"{output_file}{_info}_acc.jpg", self.accumulated_img)
        self.logger(f'Saved: "{output_file}" ')

    def write_video(self):
        while True:
            try:
                next = self.frame_queue.get_nowait() if self.read_input_done else self.frame_queue.get(timeout=2)
                self.video_writer.write(next)
            except queue.Empty:
                break

    def queue_write(self):

        self.write_video()
        self.write_image()

    def read_frames(self):
        self.read_input_done = False
        try:
            with self.frame_queue.mutex:
                self.frame_queue.queue.clear()
            self.iterate_frames()
        except Exception as e:
            self.logger(f"Failed:{repr(e)}")
            print(e)
        self.read_input_done = True

    def write_frames(self):
        time.sleep(1)
        try:
            starttime = time.perf_counter()
            height, width, layers = self.ref_frame.shape
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = f'output/{ts}.mp4'
            fps = self.output_fps  # make customizable?

            if not os.path.isdir('output'):
                os.mkdir('output')

            self.video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

            self.queue_write()

            tt = (time.perf_counter() - starttime)
            self.logger(f'Saved: "{output_file}" \n'
                        f'\tTime taken: {tt:.2f} seconds')
        except Exception as e:
            self.logger(f"Failed:{repr(e)}")
            print(e)
        finally:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            self.read_input_done = False

    def update_settings(self, settings=None):
        if settings is None:
            settings = {}

        self.intensity = int(settings[Inputs.HEAT_INTENSITY] or 2)
        self.step_size = int(settings[Inputs.FRAME_SKIP] or 0) + 1
        self.max_frames = int(settings[Inputs.MAX_FRAMES] or 0)
        self.var_threshold = int(settings[Inputs.VARIANCE_THRESHOLD] or 50)
        self.bg_history = int(settings[Inputs.HIST_FRAMES] or 100)
        self.output_fps = int(settings[Inputs.OUTPUT_FPS] or 30)
        self.erode = int(settings[Inputs.ERODE_ITERATIONS] or 0)
        self.color_map = cv2.COLORMAP_HOT
        self.shadows = True if int(settings[Inputs.DETECT_SHADOWS] or 0) else False
        self.logger(f"intensity={self.intensity},"
                    f"step_size={self.step_size},"
                    f"max_frames={self.max_frames},"
                    f"var_threshold={self.var_threshold},"
                    f"bg_history={self.bg_history},"
                    f"output_fps={self.output_fps},"
                    f"erode={self.erode},"
                    f"color_map={self.color_map},"
                    f"shadows={self.shadows},")


def load_file(path):
    hmp = HeatMapProcessor.get_instance()
    hmp.set_input_file(path)


def generate_heatmap(settings):
    hmp = HeatMapProcessor.get_instance()
    hmp.update_settings(settings)
    threading.Thread(target=hmp.read_frames).start()
    threading.Thread(target=hmp.write_frames).start()


def set_reference_frame(**kwargs):
    return HeatMapProcessor.get_instance().set_reference_frame(**kwargs)