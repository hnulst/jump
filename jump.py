import math
import subprocess
from multiprocessing import Process, Queue

from matplotlib import pyplot as plt

BASE_PATH = 'C:\\Users\\Jenny\\Desktop\\jump\\'
CAP = 'adb shell screencap -p //sdcard//jump.png'
PULL = 'adb pull //sdcard//jump.png '
LONG_CLICK = 'adb shell input swipe 500 500 510 510 '
ALPHA = 1.37

q = Queue()


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


def show(idx):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    img = plt.imread(BASE_PATH + str(idx) + '.png')
    ax.imshow(img)
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
