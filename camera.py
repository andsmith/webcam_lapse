import cv2
import os
import sys
import time
import cv2

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print ""
        print ""

        print "Syntax> python camera.py file_prefix lag_seconds_float [start_number]"
        print ""
        print "Arguments:"
        print "    file_prefix:  name to prepend image names with, e.g. frames/frame_"
        print "                  (path must exist)"
        print "    lag_seconds:  Seconds between each saved frame."
        print "    start_number:  start saving frames with this integer in the filename."
        print ""
        print "Example ffmpeg calls:"
        print "  30 FPS:  "
        print '    ffmpeg -start_number 0 -i "../camera/new_frames/frame_%08d.jpg"  -vcodec libx264 output_timelapse.mp4' 
        print "  60 FPS:  "
        print '    ffmpeg -start_number 0 -i "../camera/new_frames/frame_%08d.jpg" -filter:v "setpts=0.5*PTS" -vcodec libx264 -r 60 output.mp4'
        print ""
        sys.exit()

    ind = 0 if len(sys.argv)<4 else int(sys.argv[3])
    print "Starting with image index %i." % (ind, )

    n_decim = 8
    lag = float(sys.argv[2])
    prefix = sys.argv[1]

    path, file_prefix = os.path.split(os.path.abspath(prefix))
    if not os.path.exists(path):
        os.makedirs(path)
    print "Writing files %s_....jpg to %s" % (file_prefix, path)
    

    cap = cv2.VideoCapture(0)
    print "Resolution:  ", str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print cv2.CAP_PROP_FRAME_WIDTH, cap.set(cv2.CAP_PROP_FRAME_WIDTH,int(640))
    print cv2.CAP_PROP_FRAME_HEIGHT, cap.set(cv2.CAP_PROP_FRAME_HEIGHT,int(480));
    print cv2.CAP_PROP_FPS, cap.set(cv2.CAP_PROP_FPS, 120)

    cap.set(15, -8.0)
    time.sleep(2)

    print "Resolution: %s x %s @ %s "%( str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), cap.get(cv2.CAP_PROP_FPS))

    recording = False
    print "Recording: %s" % (recording, )
    last_t = time.time()
    frame_time = time.time()
    num_frames = 0
    while True:
        ret, frame = cap.read()
        # Display the resulting frame
        cv2.imshow('frame',frame)
        num_frames+=1
        k = cv2.waitKey(1)
        if k & 0xFF == ord('q'):
            break
        elif k & 0xFF == ord(' '):
            recording = not recording
            print "Recording: %s" % (recording, )
            if not recording:
                print "\n\thit SPACE (in image display window) to start recording..."
        elif k & 0xFF==ord('f'):
            now = time.time()
            seconds = now - frame_time
            frame_time = now
            fps = float(num_frames) / seconds
            num_frames=0
            print "Current display FPS:  %.3f" % (fps, )
        now = time.time()
        if now - last_t > lag and recording:
            out_name = os.path.join(path, "%s%.8i.jpg" % (file_prefix, ind))
            print "\tsaving frame to:  %s" % (out_name, )
            cv2.imwrite(out_name, frame)
            last_t = now
            ind += 1

cap.release()
cv2.destroyAllWindows()
