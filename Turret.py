# import statements
from adafruit_servokit import ServoKit
from board import SCL_1, SDA_1
import busio
import math

CAMERA_FOV = 105 

# Max and min angles that the servos can rotate to.
ANGLE_MIN = 0
ANGLE_MAX = 270

# How far from center a target can be.
X_COORD_CUTOFF = 50
Y_COORD_CUTOFF = 100

# Constants
MIN_PULSE_WIDTH = 500  # Hz
MAX_PULSE_WIDTH = 2500  # Hz

MAX_ACTUATION_RANGE = 270 # Degrees
X_SERVO_INDEX = 0 # Index refers to the servo controller board
Y_SERVO_INDEX = 1 # Index refers to the servo controller board

# Change this value to true when the software is run on the turret.
RUNNING_ON_JETSON = False
if(RUNNING_ON_JETSON):
    i2c = busio.I2C(SCL_1, SDA_1)
    kit = ServoKit(channels = 8, i2c = i2c, address = 0x40)

    kit.servo[0].actuation_range = MAX_ACTUATION_RANGE
    kit.servo[1].actuation_range = MAX_ACTUATION_RANGE

    kit.servo[0].set_pulse_width_range(MIN_PULSE_WIDTH, MAX_PULSE_WIDTH)
    kit.servo[1].set_pulse_width_range(MIN_PULSE_WIDTH, MAX_PULSE_WIDTH)

class Turret:  
    def __init__(self):
        self.runningOnJetson = RUNNING_ON_JETSON
        self.currentXAngle = 135
        self.currentYAngle = 135

        # Frame size information.
        self.frameWidth = 0
        self.frameHeight = 0
        self.centerX = 0
        self.centerY = 0

        # Camera information.
        self.focalLength = 1.0

        self.angleIncrement = 5

    # Set frame width
    def setFrameWidth(self, width):
        self.frameWidth = width
        self.centerX = self.frameWidth/2

    # Set frame height
    def setFrameHeight(self, height):
        self.frameHeight = height
        self.centerY = self.frameHeight/2
       
    # Sets the focal length
    def setFocalLength(self):
        if(self.frameWidth > self.frameHeight):
            self.focalLength = (self.centerX) * 1/math.tan(math.radians(CAMERA_FOV/2))
        else:
            self.focalLength = (self.centerY) * 1/math.tan(math.radians(CAMERA_FOV/2))

    # Convert the given coordinate into an angle that can be used by the servo
    # Returns the x angle to be added
    def xCoordToAngle(self, xCoord):
        angle = 0
        print("x coordinate: " + str(xCoord))
        if(abs(xCoord - self.centerX) > X_COORD_CUTOFF):
            angle = self.angleIncrement

            if((self.centerX - xCoord) < 0):
                angle *= -1
        else:
            print("Target is close enough (x direction)")

        return angle
        
   
    # Convert the given coordinate into an angle that can be used by the servo
    # Returns the y angle to be added
    def yCoordToAngle(self, yCoord):
        angle = 0
        print("y coordinate: " + str(yCoord))
        if(abs(yCoord - self.centerY) > Y_COORD_CUTOFF):
            angle = self.angleIncrement

            if((self.centerY - yCoord) < 0):
                angle *= -1
        else:
            print("Target is close enough (y direction)")
        return angle

    # Take in coordinates and set turret to point to those coordinates
    def setToCoord(self, x, y):
        
        xAngle = self.xCoordToAngle(x)
        yAngle = self.yCoordToAngle(y)

        print(str(self.currentXAngle) + " is the current X angle")
        print(str(self.currentYAngle) + " is the current Y angle")

        print(str(xAngle) + " is the X angle to be added")
        print(str(xAngle) + " is the Y angle to be added")

        xAngle += self.currentXAngle
        yAngle += self.currentYAngle

        print(str(xAngle) + " is the new X angle")
        print(str(yAngle) + " is the new Y angle")

        if(xAngle < ANGLE_MAX and xAngle > ANGLE_MIN):
            # Update current angle
            self.currentXAngle = xAngle

            if(self.runningOnJetson):
                kit.servo[X_SERVO_INDEX].angle = xAngle

            print("Expected X Angle: " + str(xAngle))
        else:
            print("X angle " + str(xAngle) + " was too large, refusing...")

        if(yAngle < ANGLE_MAX and yAngle > ANGLE_MIN):
            # Update current angle
            self.currentYAngle = yAngle

            if(self.runningOnJetson):
                kit.servo[Y_SERVO_INDEX].angle = yAngle

            print("Expected Y Angle: " + str(yAngle))
        else:
            print("Y angle " + str(yAngle) + " was too large, refusing...")
    
