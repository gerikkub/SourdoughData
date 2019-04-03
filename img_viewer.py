import cv2
import serial
import time
import os
import math

from multiprocessing import Process


class Logger():

    def __init__(self, devices, log_dir):

        self._f = open(os.path.join(log_dir, 'data.csv'), 'w')

        self._devices = devices


    def write_header(self):

        self._f.write('timestamp,' + ','.join(self._devices) + '\n')

    def write_data(self, temps):

        curr_ts = time.time()

        self._f.write(str(curr_ts))

        for dev in self._devices:
            self._f.write(',' + str(temps[dev]))

        self._f.write('\n')

        self._f.flush()

def read_until_str(ser, string):

    data = bytes()

    while data[-1*len(string):] != string.encode('utf-8'):
        data = data + ser.read(1)

    return data

def captureTemps(log_dir, serialDev):

    ser = serial.Serial(serialDev, 115200)

    ser.reset_input_buffer()

    data = read_until_str(ser, 'DONE\r\n')

    data = read_until_str(ser, 'DONE\r\n')


    try:
        data_str = data.decode('utf-8')
    except:
        print("Error decoding data")
        return

    devices = []

    lines = data_str.split('\r\n')
    for line in lines:
        if ':' in line:
            device, temp = line.split(': ')

            devices.append(device)

    log = Logger(devices, log_dir)

    log.write_header()

    while True:
        data = read_until_str(ser, 'DONE\r\n')

        try:
            data_str = data.decode('utf-8')
        except:
            print("Error decoding data")
            continue

        curr_time = time.time()
        print('Got temp data at {}', curr_time)

        temps = {}

        lines = data_str.split('\r\n')
        for line in lines:
            if ':' in line:
                device, temp = line.split(': ')

                temps[device] = temp

        log.write_data(temps)

def captureImages(log_dir):

    cap = cv2.VideoCapture(0)

    img_num = 0

    while True:
        ret, frame = cap.read()

        img_time = math.floor(time.time())

        img_name = "{}_{}_img.jpg".format(img_num, img_time)
        print('Captured ' + img_name)
        cv2.imwrite(img_name, frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1000 * 60 * 5) & 0xFF == ord('q'):
            break

        img_num += 1

    cap.release()
    cv2.destroyAllWindows()

temp_p = Process(target=captureTemps, args=('.', '/dev/cu.usbmodem0007783385771'))
img_p = Process(target=captureImages, args=('.'))

temp_p.start()
img_p.start()

while True:
    time.sleep(1)
