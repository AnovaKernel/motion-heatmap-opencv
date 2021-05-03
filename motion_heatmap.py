import copy
import datetime
import os.path
import queue
import time

import cv2
import numpy as np

from util import *


class HeatMapProcessor(object):

    def __init__(self, input_file, entries=None, logger=None) -> None:
        super().__init__()

        self.capture = cv2.VideoCapture(input_file)
        self.background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
        self.length = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.logger = logger
        self.video_writer = None
        self.ref_frame = None
        self.frame_queue = queue.Queue()
        self.accumulated_img = None
        # self.get_reference_frame()
        self.read_input_done = False

        if entries is None:
            entries = {}
        self.max_value = int(entries[HEAT_INTENSITY].get() or 3)
        self.step_size = int(entries[FRAME_SKIP].get() or 0) + 1
        self.max_frames = int(entries[MAX_FRAMES].get() or 0)

    def get_reference_frame(self):
        # todo: allow to input a custom reference frame
        _, frame = self.capture.read()
        self.ref_frame = copy.deepcopy(frame)
        self.accumulated_img = np.zeros(self.ref_frame.shape[:2], np.uint8)
        h, w, _ = self.ref_frame.shape
        self.logger(f'Reference Frame Loaded ({w}x{h})')

    def iterate_frames(self):

        start_ms = round(time.time() * 1000)
        start_dt = datetime.datetime.now()

        threshold = 2
        # handles color intensity
        max_value = self.max_value
        step_size = self.step_size
        last_frame = min(self.length - 1, self.max_frames * step_size) if self.max_frames > 0 else self.length - 1
        frames_read = 0

        self.logger(f'Processing {int(last_frame / step_size)} frames\n'
                    f'\tstep={step_size}\n'
                    f'\tmax_frames={self.max_frames}\n'
                    f'\tintensity={max_value}\n')
        for i in range(0, last_frame, step_size):
            # account for step_size by setting capture frame position
            if step_size > 1:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, i)

            ret, frame = self.capture.read()

            if not ret:
                break

            frames_read += 1
            background_filter = self.background_subtractor.apply(frame)  # remove the background

            ret, th1 = cv2.threshold(background_filter, threshold, max_value, cv2.THRESH_BINARY)

            # add to the accumulated image
            self.accumulated_img = cv2.add(self.accumulated_img, th1)

            color_image = cv2.applyColorMap(self.accumulated_img, cv2.COLORMAP_HOT)
            # frame*alpha+color_image*beta+gamma
            video_frame = cv2.addWeighted(frame, 0.7, color_image, 0.6, 0)

            self.frame_queue.put(video_frame)

            if (i + step_size) % (step_size * 10) == 0:
                avg_frame_time = ((round(time.time() * 1000) - start_ms) / frames_read)
                to_go = int(last_frame / step_size) - frames_read

                self.logger(f'[{round(i / last_frame * 100)}%] '
                            f'[{to_go} remaining] '
                            f'[{int(avg_frame_time)} ms/frame] '
                            f'ETA: [{round(to_go * avg_frame_time / 1000)} sec.]', status_only=True)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        tt = (datetime.datetime.now() - start_dt)
        logentry = f'Done. {frames_read} frames read in {int(tt.total_seconds())} seconds'
        self.logger(logentry, status_only=True)
        self.logger(logentry)

    def write_image(self):
        color_image = cv2.applyColorMap(self.accumulated_img, cv2.COLORMAP_HOT)
        result_overlay = cv2.addWeighted(self.ref_frame, 0.7, color_image, 0.7, 0)

        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f'output/{ts}.jpg'

        # save the final heatmap
        cv2.imwrite(output_file, result_overlay)
        self.logger(f'Saved: "{output_file}" ')

    def write_video(self):
        while True:
            try:
                next = self.frame_queue.get_nowait() if self.read_input_done else self.frame_queue.get()
                self.video_writer.write(next)  # self.frame_queue.task_done()
            except queue.Empty:
                break

    def queue_read(self):
        self.iterate_frames()
        pass

    def queue_write(self):

        self.write_video()
        self.write_image()

    def read_frames(self):
        self.read_input_done = False

        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()

        self.get_reference_frame()
        self.iterate_frames()

        self.read_input_done = True

    def write_frames(self):
        time.sleep(2)
        starttime = datetime.datetime.now()
        height, width, layers = self.ref_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f'output/{ts}.avi'
        fps = 30.0  # make customizable?

        if not os.path.isdir('output'):
            os.mkdir('output')

        self.video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        self.queue_write()

        cv2.destroyAllWindows()
        self.video_writer.release()
        tt = (datetime.datetime.now() - starttime)
        self.logger(f'Saved: "{output_file}" \n'
                    f'\tTime taken: {int(tt.total_seconds())} seconds')