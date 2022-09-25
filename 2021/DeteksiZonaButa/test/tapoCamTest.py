from imutils import resize
from time import sleep
import cv2

WIN_NAME = 'TapoCam_C310'
VIDEO_SRC = 'rtsp://tapocam:t.p.c.m@192.168.43.178:554/stream1'
MAX_WIDTH = 640
MAX_HEIGHT = 360

def main():
    def stop(vStream):
        try:
            print('Exiting...')
            cv2.destroyAllWindows()
            vStream.release()
            exit()
        except Exception as e:
            print('Forced exit!', e)
            exit()
    
    vStream = cv2.VideoCapture(VIDEO_SRC)

    try:
        sleep(1)
        while(True):
            r, frame = vStream.read()
            frame = resize(frame, width=MAX_WIDTH, height=MAX_HEIGHT)
            cv2.imshow(WIN_NAME, frame)
            if ord('q') == cv2.waitKey(10):
                stop(vStream)
    except KeyboardInterrupt:
        stop(vStream)
    except Exception as e:
        print('Exception!'. e)
        exit()

if __name__ == '__main__':
    main()
