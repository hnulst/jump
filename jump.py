import math
import subprocess
from multiprocessing import Process, Queue

import cv2
from matplotlib import pyplot as plt

BASE_PATH = 'C:\\Users\\Jenny\\Desktop\\jump\\'
CAP = 'adb shell screencap -p //sdcard//jump.png'
PULL = 'adb pull //sdcard//jump.png '
LONG_CLICK = 'adb shell input swipe 500 500 510 510 '
ALPHA = 1.37

TM_METHOD = 'cv2.TM_CCOEFF'

q = Queue()
template = cv2.imread('C:\\Users\\Jenny\\Desktop\\jump\\ren.png', 0)
w, h = template.shape[::-1]


def coor_to_time(coor):
    (x0, y0) = coor[0]
    (x1, y1) = coor[1]
    dist = math.sqrt((x0 - x1) * (x0 - x1) + (y0 - y1) * (y0 - y1))
    # print('dist = %.2f' % (dist))
    return (int)(ALPHA * dist)


def jump(q):
    idx = 0
    coor = [(0, 0), (1, 1)]
    while True:
        idx = idx % 2
        coor[idx] = q.get(True)
        if idx == 1:
            jump_cmd = LONG_CLICK + str(coor_to_time(coor))
            # print(jump_cmd)
            run_cmd(jump_cmd)
        idx += 1


def onclick(event):
    x, y = event.xdata, event.ydata
    q.put((x, y))
    print('(%.2f, %.2f)' % (x, y))


def match(img, template):
    res = cv2.matchTemplate(img, template, eval(TM_METHOD))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img, top_left, bottom_right, 255, 2)
    x = top_left[0] + w / 2
    y = bottom_right[1] - h / 10
    cv2.circle(img, ((int)(x), (int)(y)), 3, (0, 0, 255), -1)
    q.put((x, y))


def show(idx):
    fig = plt.figure()
    fig.add_subplot(111)
    img = cv2.imread(BASE_PATH + str(idx) + '.png', 0)
    match(img, template)
    plt.imshow(img, cmap='gray'), plt.title(str(idx))
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()


def run_cmd(cmd):
    subprocess.check_call(cmd)


if __name__ == '__main__':
    idx = 1
    jump_process = Process(target=jump, args=(q,))
    jump_process.start()
    while True:
        if idx == 1:
            input()
        run_cmd(CAP)  # screencap
        print('capturing ' + str(idx) + '.png\n')
        run_cmd(PULL + BASE_PATH + str(idx) + '.png')
        # show it in window
        show(idx)
        idx += 1
