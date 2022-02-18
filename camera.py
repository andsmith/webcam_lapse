"""
Generate time-lapse videos using a webcam.
(this script generates frames for creating a video with, e.g., ffmpeg)
"""

import cv2
import os
import numpy as np
import time
import cv2
import argparse
import sys
from webcam_res import pick_resolution


class WebcamLapse(object):
    """
    Timelapse camera object.
    """

    def __init__(self, file_prefix, lag_seconds, start_number=0, camera_index=0, resolution=None, digits=8,
                 img_ext="jpg"):
        """
        Start camera, not recording.
        :param file_prefix:  How to name frames, can include path, examples:  "frame_" "video/frame_"
        :param lag_seconds:  Number of seconds between frames. (float)
        :param start_number:  index of first frame (for saving)
        :param camera_index:  which camera to use?
        :param resolution:  (width, height)
        :param digits: Number of decimal places, e.g. file_prefix="frame_", with 5 digits yields:
            frame_00000.png
            frame_00001.png ...
        :param img_ext: extension of image files.
        """

        self._cam_index = camera_index
        self._lag = lag_seconds
        self._digits = digits
        self._prefix = file_prefix
        self._target_resolution = resolution
        self._ind_start = start_number
        self._ind = self._ind_start
        self._img_ext = img_ext

        while np.log10(self._ind_start) >= self._digits:
            self._digits += 1

        self._cam_params = {}  # enum: value
        self._init_camera()

    def _set_camera_res(self):
        """
        Set camera to whatever the current target is.
        :return:
        """
        print("Current resolution:  %s x %s" % (
              str(self._cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
              str(self._cam.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        if self._target_resolution is not None:
            width, height = self._target_resolution
            self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            print("New resolution: %s x %s" % (
                str(self._cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
                str(self._cam.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        else:
            print("No target resolution, camera not changed.")

    def _init_camera(self):
        """
        Open camera, set program start state, build filenames
        """
        system = 'win' if sys.platform in ["win32"] else "linux"

        print("Starting with image index %i." % (self._ind,))

        self._path, self._file_prefix = os.path.split(os.path.abspath(self._prefix))
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        print(self._sub_digit_str("First frame will be %s%i.%s, written to to %s") % (self._file_prefix,
                                                                  self._ind,
                                                                  self._img_ext,
                                                                  self._path))
        if system == "win":
            print("Windows OS detected, attempting clean camera open...")
            self._cam = cv2.VideoCapture(self._cam_index, cv2.CAP_DSHOW)
        else:
            self._cam = cv2.VideoCapture(self._cam_index)
        self._recording = False
        self._set_camera_res()

    def start(self):
        """
        Start grabbing frames, reading keyboard input, etc.\
        """
        print("Recording (hit space on image window to toggle): %s" % (self._recording,))
        last_t = time.time()
        frame_time = time.time()
        num_frames = 0
        while True:
            ret, frame = self._cam.read()
            if not ret or frame is None:
                print("Warning, no data received...")
                time.sleep(0.2)

            # Display the resulting frame
            cv2.imshow('frame', frame)
            num_frames += 1
            k = cv2.waitKey(1)
            if k & 0xFF == ord('q'):
                break
            elif k & 0xFF == ord(' '):
                self._recording = not self._recording
                print("Recording: %s" % (self._recording,))
            elif k & 0xFF == ord('f'):
                now = time.time()
                seconds = now - frame_time
                frame_time = now
                fps = float(num_frames) / seconds
                num_frames = 0
                print("Current display FPS:  %.3f" % (fps,))
            now = time.time()
            if now - last_t > self._lag and self._recording:
                out_name = os.path.join(self._path,
                                        self._sub_digit_str("%%s%%i.%s" % (self._img_ext,)) % (
                                            self._file_prefix, self._ind))
                print("\tsaving frame to:  %s" % (out_name,))
                cv2.imwrite(out_name, frame)
                last_t = now
                self._ind += 1
                if np.log10(self._ind) >= self._digits:
                    self._digits += 1

        self._cam.release()
        cv2.destroyAllWindows()
        print("\nRecording stopped.\nCamera shutdown.")

    def _sub_digit_str(self, string, fmt="%%.%ii"):
        """
        Repair a string format from integers, to integers with the correct number of leading zeros
        :param string:
        :param fmt:
        :return:
        """
        return string.replace("%i", fmt % (self._digits,))

    def print_ffmpeg_instructions(self):
        time.sleep(1)
        print("\n\nExample ffmpeg calls to combine frames into a video:")
        print("""
        30 FPS:
            ffmpeg -start_number %s -i "%s_0%id.%s"  -vcodec libx264 output_timelapse.mp4

        60 FPS:  
           ffmpeg -start_number %s -i "%s_0%id.%s" -filter:v "setpts=0.5*PTS" -vcodec libx264 -r 60 output.mp4'
""" % (self._ind_start, self._prefix, self._digits, self._img_ext, self._ind_start, self._prefix, self._digits,
       self._img_ext,))


def do_args():
    parser = argparse.ArgumentParser(description="Timelapse videos using webcams.")
    parser.add_argument("file_prefix", help="Prefix for each frame, can include paths.", default="frame_")
    parser.add_argument("lag_seconds", help="Delay between each frame", default=15, type=int)
    parser.add_argument("start_number", help="Start frame indices with this value.", default=0, type=int)
    parser.add_argument("--camera_index", "-c", help="Device index", default=0)
    parser.add_argument("--type", "-t", help="Either 'png' or 'jpg'", default='jpg')
    parser.add_argument("--resolution", "-r", help="WIDTHxHEIGHT set to this resolution.", default="", type=str)
    parser.add_argument("--select_resolution", "-s", help="chose resolution interactively", action='store_true',
                        default=False)
    parser.add_argument("--digits", "-d", help="Number of leading zeros for frames (increased if exceeded)",
                        default=8, type=int)
    parsed = parser.parse_args()
    if parsed.type not in ['jpg', 'png']:
        raise Exception("image type must be jpg or png")
    return parsed


def _split_res(res_string):
    parts = res_string.split('x')
    return int(parts[0]), int(parts[1]
                              )


if __name__ == "__main__":
    args = do_args()

    if args.select_resolution:
        resolution = pick_resolution(args.camera_index)
        if resolution is None:
            print("User exit.")
            sys.exit(0)
    elif args.resolution == "":
        resolution = None  # use default resolution
    else:
        resolution = _split_res(args.resolution)

    camera = WebcamLapse(file_prefix=args.file_prefix,
                         lag_seconds=args.lag_seconds,
                         start_number=args.start_number,
                         camera_index=args.camera_index,
                         resolution=resolution,
                         digits=args.digits,
                         img_ext=args.type)
    camera.start()
    camera.print_ffmpeg_instructions()
