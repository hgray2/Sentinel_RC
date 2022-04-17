from pyPS4Controller.controller import Controller
from adafruit_servokit import ServoKit
import time
import numpy as np
from board import SCL_1, SDA_1
import busio
import cv2

# Constants
MIN_PULSE_WIDTH = 500  # Hz
MAX_PULSE_WIDTH = 2500  # Hz

MAX_ACTUATION_RANGE = 270 # Degrees
X_SERVO_INDEX = 0 # Index refers to the servo controller board
Y_SERVO_INDEX = 1 # Index refers to the servo controller board

# Creation of servo kit
i2c = busio.I2C(SCL_1, SDA_1)
kit = ServoKit(channels = 8, i2c = i2c, address = 0x40)

kit.servo[0].actuation_range = MAX_ACTUATION_RANGE
kit.servo[1].actuation_range = MAX_ACTUATION_RANGE

kit.servo[0].set_pulse_width_range(MIN_PULSE_WIDTH, MAX_PULSE_WIDTH)
kit.servo[1].set_pulse_width_range(MIN_PULSE_WIDTH, MAX_PULSE_WIDTH)

INITIAL_X_ANGLE = 135
INITIAL_Y_ANGLE = 135

kit.servo[X_SERVO_INDEX].angle = INITIAL_X_ANGLE
kit.servo[Y_SERVO_INDEX].angle = INITIAL_Y_ANGLE

# YOLO Constants
NAMES = "../YOLO/coco.names"
CONFIG = "../YOLO/yolov3-tiny.cfg"
WEIGHTS = "../YOLO/yolov3-tiny.weights"

# Minimum confidence score required for detection
MIN_CONFIDENCE_SCORE = 0.3

# YOLO 
net = cv2.dnn.readNet(WEIGHTS, CONFIG)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# Read labels from coco.names
labels = []
with open (NAMES, 'r') as names:
    for name in names:
        label = name.strip("\n")
        labels.append(label)


# Read in output layers from net
layerNames = net.getLayerNames()

outputLayers = []

for index in net.getUnconnectedOutLayers():
    index = index[0]
    outputLayers.append(layerNames[index - 1]) 


class Teleop(Controller):
    
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.currentXAngle = INITIAL_X_ANGLE
        self.currentYAngle = INITIAL_Y_ANGLE
        self.incrementAngle = 5
          
    # Y Axis
    def on_up_arrow_press(self):
        if(self.currentYAngle + self.incrementAngle < MAX_ACTUATION_RANGE):
            kit.servo[Y_SERVO_INDEX].angle = self.currentYAngle + self.incrementAngle
            self.currentYAngle += self.incrementAngle
    
    def on_down_arrow_press(self):
        if(self.currentYAngle - self.incrementAngle > 0):
            kit.servo[Y_SERVO_INDEX].angle = self.currentYAngle - self.incrementAngle
            self.currentYAngle -= self.incrementAngle

    # X Axis
    def on_left_arrow_press(self):   
        if(self.currentXAngle + self.incrementAngle < MAX_ACTUATION_RANGE):     
            kit.servo[X_SERVO_INDEX].angle = self.currentXAngle + self.incrementAngle
            self.currentXAngle += self.incrementAngle 

    def on_right_arrow_press(self, **kwargs):
        if(self.currentXAngle - self.incrementAngle > 0):
            kit.servo[X_SERVO_INDEX].angle = self.currentXAngle - self.incrementAngle
            self.currentXAngle -= self.incrementAngle

    def on_R1_press(self):
        self.incrementAngle += 1
        print(self.incrementAngle)

    def on_L1_press(self):
        self.incrementAngle -= 1
        print(self.incrementAngle)

    # Reset button
    def on_x_press(self, **kwargs):
        kit.servo[X_SERVO_INDEX].angle = INITIAL_X_ANGLE
        self.currentXAngle = INITIAL_X_ANGLE
        kit.servo[Y_SERVO_INDEX].angle = INITIAL_Y_ANGLE
        self.currentYAngle = INITIAL_Y_ANGLE
         


if __name__ == "__main__":

    teleop = Teleop(interface="/dev/input/js0", connecting_using_ds4drv=False)
    teleop.listen(timeout=60)
    
