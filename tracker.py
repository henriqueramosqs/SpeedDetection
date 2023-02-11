import cv2 as cv
import numpy as np
from vehicule import *
import math

MIDDLE_RAY = 700
LOW_POINT_RIGHT_POLY = 576
TOP_LINE_RIGHT = 370
BOTTOM_LINE_RIGHT = 390
MAX_DIST = 70
FPS = 30

class Tracker:
    def __init__(self):
        self.vehs = []
        self.count = 0
    
    def update(self, cx, cy, frame, inRoi):
        found = False
        for veh in self.vehs:
            #Calculating distance from previously found objects.
            dist = math.sqrt((cx - veh.cx)**2 + (cy - veh.cy)**2)
            #If distance less than an empiric value, it means that its the same vehicle.
            if(dist < MAX_DIST):
                found = True
                match = veh
                break
        #If found, it means that it's an already detected vehicle.
        if found:
            #Updating values for vehicule ID.
            if inRoi:
                match.update(cx,cy)
                match.setFinal(frame)
                return match.id,0
            else:
                if cy > BOTTOM_LINE_RIGHT:
                    match.update(cx,cy)
                    if(match.speed == -1):
                        match.setSpeed(60)
                    return match.id,match.speed
                else:
                    print("--------------removed---------------")
                    self.vehs.remove(match)
                    return -1,-1
        else:
            #It's a new vehicle.
            if inRoi:
                self.count += 1
                newVeh = Vehicule(cx,cy,self.count,frame)
                self.vehs.append(newVeh)
                return newVeh.id,0
            return -1,-1
        
    def getAmount(self):
        print(len(self.vehs))
        return self.count
    
    def clean(self):
        self.vehs = []
        