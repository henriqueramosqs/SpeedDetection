import cv2 as cv
import numpy as np
from vehicule import *
import math

MIDDLE_RAY = 650
LOW_POINT_RIGHT_POLY = 576
TOP_LINE_RIGHT = 370
BOTTOM_LINE_RIGHT = 390
MAX_DIST = 20
FPS = 30

class Tracker:
    def __init__(self):
        self.cur = []
        self.prev = []
        self.count = 0

    def update(self, detected, frame):
        self.cur = detected
        temp = []
        out = []
        for cveh in self.cur:
            x,y,w,h,inRoi = cveh
            
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            found = False
            
            for pveh in self.prev:
            #Calculating distance from previously found objects.
                dist = math.sqrt((cx - pveh.cx)**2 + (cy - pveh.cy)**2)
                if(dist < MAX_DIST):
                    found = True
                    match = pveh
                    break  
            if found:
                #Updating values for vehicule ID.
                if inRoi:
                    match.update(cx,cy)
                    match.setFinal(frame)
                    temp.append(match)
                    out.append((match.id,0))
                else:
                    if cy > BOTTOM_LINE_RIGHT:
                        match.update(cx,cy)
                        if(match.speed == -1):
                            match.setSpeed(FPS)
                        temp.append(match)
                        out.append((match.id,match.speed))
                    else:
                        out.append((-1,-1))
            else:
                #It's a new vehicle.
                if inRoi:
                    self.count += 1
                    #print("create ",self.count,self.aux,inRoi,cx,cy)
                    newVeh = Vehicule(cx,cy,self.count,frame)
                    temp.append(newVeh)
                    out.append((newVeh.id,0))
                else:
                    out.append((-1,-1))
        
        self.prev = temp
        return out
        
    def getAmount(self):
        return self.count
    
    def clean(self):
        self.curvehs = []