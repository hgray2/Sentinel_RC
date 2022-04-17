# Import statements
import numpy as np
import argparse
import time
import cv2
import os
from Turret import Turret

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

def readFrame(frame,turret,frameDelay):
    # OpenCV information
    FONT = cv2.FONT_HERSHEY_PLAIN
    FONT_SCALE = 1.5
    starting_time = time.time()
    frame_id = 0
    
    # Rotates the camera 90 degrees clockwise if this script is run on the turret.
    if(turret.runningOnJetson == True):
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    frame_id += 1

    height,width,channels = frame.shape    

    turret.setFrameWidth(width)
    turret.setFrameHeight(height)

    turret.setFocalLength()

    blob = cv2.dnn.blobFromImage(frame,scalefactor = 0.00392,size = (320,320),mean = (0,0,0),swapRB = True,crop=False)
    net.setInput(blob)
    outs = net.forward(outputLayers)

    class_ids=[]
    confidences=[]
    boxes=[]

    CONFIDENCE_THRESHOLD = 0.5
    NMS_THRESHOLD = 0.4

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > MIN_CONFIDENCE_SCORE and class_id == 0: # Only output when it detects a person
                centerX = int(detection[0] * width)
                centerY = int(detection[1] * height)

                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(centerX - w/2)
                y = int(centerY - h/2)

                boxes.append([x,y,w,h])
                confidences.append(float(confidence))
                class_ids.append(class_id) 

    # Filter boxes using non-maximum supression
    indices = cv2.dnn.NMSBoxes(boxes,confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    width_max = 0
    x_max = 0
    y_max = 0
    for i in range(len(boxes)):
        if i in indices:
            x,y,w,h = boxes[i]

            label = str(labels[class_ids[i]])
            confidence = confidences[i]

            # Draw Bounding Boxes
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,0) ,2)
            cv2.putText(frame,label+" "+str(round(confidence,2)),(x,y+20),FONT,FONT_SCALE,(255,255,255),2)

            centerX = int(x + w/2)
            centerY = int(y + h/2)  

            # Draw Targets
            if (frameDelay == 10):
                cv2.circle(frame,(centerX,centerY), 5, (255,255,255), 2)

            # This might be a very simple way to handle multiple targets on the screen at once.
            # TODO: Test it.
            if(w > width_max):
                width_max = x

                x_max = centerX
                y_max = centerY

    if (x_max != 0 and y_max != 0 and frameDelay == 1):
        targetHandler(frame, turret, x_max, y_max)

    # Calculate and display FPS
    elapsed_time = time.time() - starting_time
    fps = frame_id/elapsed_time
    cv2.putText(frame,"FPS:" + str(round(fps,2)),(10,50),FONT,FONT_SCALE,(0,0,0),2)
    
    cv2.imshow('Sentinel', frame)

def targetHandler(frame, turret, x_max, y_max):
    cv2.circle(frame,(x_max,y_max), 5, (255,0,0), 2)
    turret.setToCoord(x_max,y_max)

if __name__ == "__main__" :

    # Access Camera
    try:
        capture = cv2.VideoCapture(0)
    except:
        print("Error: cannot access camera")

    turret = Turret()

    #video = cv2.VideoCapture("/home/hayden/Downloads/sample.mp4")
    frameDelay = 0
    while True:
        _ , frame = capture.read()

        readFrame(frame,turret,frameDelay)

        # Reset or incremement frame counter
        if(frameDelay == 1):
            frameDelay = 0
        else: 
            frameDelay += 1
      
        key = cv2.waitKey(1)

        if (key == 27):    # Esc key to stop
            turret.shutdownGPIO()
            break
