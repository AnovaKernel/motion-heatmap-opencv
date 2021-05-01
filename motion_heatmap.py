import copy

import cv2
import numpy as np


class HeatMap(object):

    def __init__(self, input_file) -> None:
        super().__init__()
        self.capture = cv2.VideoCapture(input_file)
        self.background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
        self.length = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

        self.ref_frame = None
        self.video_frames = []
        self.accumulated_img = None

    def get_reference_frame(self):
        # todo: allow to input a custom reference frame
        _, frame = self.capture.read()
        self.ref_frame = copy.deepcopy(frame)
        self.accumulated_img = np.zeros(self.ref_frame.shape[:2], np.uint8)

    def iterate_frames(self):

        if not self.ref_frame:
            self.get_reference_frame()

        threshold = 2
        maxValue = 5

        for i in range(0, self.length - 1):

            ret, frame = self.capture.read()

            filter = self.background_subtractor.apply(frame)  # remove the background

            ret, th1 = cv2.threshold(filter, threshold, maxValue, cv2.THRESH_BINARY)

            # add to the accumulated image
            self.accumulated_img = cv2.add(self.accumulated_img, th1)

            color_image_video = cv2.applyColorMap(self.accumulated_img, cv2.COLORMAP_SUMMER)
            video_frame = cv2.addWeighted(frame, 0.7, color_image_video, 0.7, 0)
            self.video_frames.append(video_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def make_image(self):

        if not self.accumulated_img:
            self.iterate_frames()

        color_image = cv2.applyColorMap(self.accumulated_img, cv2.COLORMAP_HOT)
        result_overlay = cv2.addWeighted(self.ref_frame, 0.7, color_image, 0.7, 0)

        # save the final heatmap
        cv2.imwrite('heatmap-overlay.jpg', result_overlay)

    def make_video(self):

        if not self.video_frames:
            self.iterate_frames()

        images = self.video_frames

        height, width, layers = self.ref_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        video = cv2.VideoWriter('output.avi', fourcc, 30.0, (width, height))

        print(f'Creating Video {len(images)}')

        for image in images:
            video.write(image)
        cv2.destroyAllWindows()
        video.release()
