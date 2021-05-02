import copy
import datetime
import os.path
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

        self.ref_frame = None
        self.video_frames = None
        self.accumulated_img = None
        self.get_reference_frame()

        if entries is None:
            entries = {}
        self.max_value = int(entries[HEAT_INTENSITY].get() or 3)
        self.step_size = int(entries[FRAME_SKIP].get() or 0) + 1
        self.max_frames = int(entries[MAX_FRAMES].get() or 4000)

    def get_reference_frame(self):
        # todo: allow to input a custom reference frame
        _, frame = self.capture.read()
        self.ref_frame = copy.deepcopy(frame)
        self.accumulated_img = np.zeros(self.ref_frame.shape[:2], np.uint8)

    def iterate_frames(self):

        self.video_frames = []

        if self.ref_frame is None:
            self.get_reference_frame()

        threshold = 2
        # handles color intensity
        max_value = self.max_value
        step_size = self.step_size
        last_frame = min(self.length - 1, self.max_frames * step_size)
        start_ms = round(time.time() * 1000)
        start_dt = datetime.datetime.now()
        frames_read = 0
        self.logger(f'Reading every {step_size}(st/nd/rd/th) frame of {self.length} frames')
        for i in range(0, last_frame, step_size):
            # account for step_size by setting capture frame position
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = self.capture.read()

            if not ret:
                break

            frames_read += 1
            background_filter = self.background_subtractor.apply(frame)  # remove the background

            ret, th1 = cv2.threshold(background_filter, threshold, max_value, cv2.THRESH_BINARY)

            # add to the accumulated image
            self.accumulated_img = cv2.add(self.accumulated_img, th1)

            color_image_video = cv2.applyColorMap(self.accumulated_img, cv2.COLORMAP_HOT)
            video_frame = cv2.addWeighted(frame, 0.7, color_image_video, 0.7, 0)

            self.video_frames.append(video_frame)

            if (i + step_size) % (step_size * 10) == 0:
                avg_frame_time = ((round(time.time() * 1000) - start_ms) / frames_read)
                to_go = last_frame - frames_read

                self.logger(
                    f'[{i + 1}/{last_frame}] {round(i / last_frame * 100)}% done. '
                    f'Average frame time: {int(avg_frame_time)} ms.',
                    status_only=True)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.logger(f'[{last_frame}/{last_frame}] 100% done. 0 seconds remaining', status_only=True)
        tt = (datetime.datetime.now() - start_dt)
        self.logger(f'Done\n'
                    f'Frames read: {frames_read}\n'
                    f'Time Taken: {int(tt.total_seconds())} seconds')

    def make_image(self):
        if not self.video_frames:
            self.iterate_frames()

        color_image = cv2.applyColorMap(self.accumulated_img, cv2.COLORMAP_HOT)
        result_overlay = cv2.addWeighted(self.ref_frame, 0.7, color_image, 0.7, 0)

        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f'output/{ts}.jpg'

        # save the final heatmap
        cv2.imwrite(output_file, result_overlay)
        self.logger(f'"{output_file}" saved')

    def make_video(self):

        if not self.video_frames:
            self.iterate_frames()
        if not os.path.isdir('output'):
            os.mkdir('output')

        starttime = datetime.datetime.now()

        images = self.video_frames

        height, width, layers = self.ref_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f'output/{ts}.avi'
        video = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height))

        self.logger(f'Writing {output_file}')
        for image in images:
            video.write(image)
        cv2.destroyAllWindows()
        video.release()
        tt = (datetime.datetime.now() - starttime)
        self.logger(f'"{output_file}" saved\n'
                    f'\tTime taken: {int(tt.total_seconds())} seconds')