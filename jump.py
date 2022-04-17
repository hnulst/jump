import math
import os
import subprocess
import sys
import time
from multiprocessing import Process, Queue

import cv2
from matplotlib import pyplot as plt

BASE_PATH = sys.path[0]
CAP = 'adb shell screencap -p //sdcard//jump.png'
PULL = 'adb pull //sdcard//jump.png '
LONG_CLICK = 'adb shell input swipe 500 500 510 510 '
ALPHA = 1.07

TM_METHOD = 'cv2.TM_CCOEFF'

coor_queue = Queue()
template = cv2.imread(filename=os.path.join(BASE_PATH, 'ren.png'), flags=0)
w, h = template.shape[::-1]

fig = plt.figure()
fig.add_subplot(111)


def on_click(event):
    x, y = event.xdata, event.ydata
    coor_queue.put((x, y))
    print('to (%.2f, %.2f)' % (x, y))
    capture()
    show()


fig.canvas.mpl_connect(s='button_press_event', func=on_click)


def coor_to_time(coor):
    (x0, y0) = coor[0]
    (x1, y1) = coor[1]
    dist = math.sqrt((x0 - x1) * (x0 - x1) + (y0 - y1) * (y0 - y1))
    # print('dist = %.2f' % (dist))
    return int(ALPHA * dist)


def jump(cq):
    idx = 0
    coor = [(0, 0), (1, 1)]
    while True:
        idx = idx % 2
        coor[idx] = cq.get(True)
        if idx == 1:
            jump_cmd = LONG_CLICK + str(coor_to_time(coor))
            # print(jump_cmd)
            run_cmd(jump_cmd)
        idx += 1


def match(img):
    res = cv2.matchTemplate(image=img, templ=template, method=eval(TM_METHOD))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img=img, pt1=top_left, pt2=bottom_right, color=255, thickness=2)
    x = top_left[0] + w / 2
    y = bottom_right[1] - h / 10
    cv2.circle(img=img, center=(int(x), int(y)), radius=3, color=(0, 0, 255), thickness=-1)
    print('from (%.2f, %.2f)' % (x, y))
    coor_queue.put((x, y))


def show():
    img = cv2.imread(filename=os.path.join(BASE_PATH, '.png'), flags=0)
    match(img)
    plt.imshow(img, cmap='gray')
    plt.show()


def capture():
    time.sleep(3)

    run_cmd(CAP)  # screencap
    print('capturing ' + os.path.join(BASE_PATH, '.png'))
    run_cmd(PULL + os.path.join(BASE_PATH, '.png'))


def run_cmd(cmd):
    subprocess.check_call(cmd)


if __name__ == '__main__':
    jump_process = Process(target=jump, args=(coor_queue,))
    jump_process.start()
    while True:
        capture()
        show()
