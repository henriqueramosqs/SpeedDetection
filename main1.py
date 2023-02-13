import cv2 as cv
import numpy as np
from tracker import *

BOX_COLOR_OKAY = (0,255,0)
BOX_COLOR_OVER = (0,0,255)
BOX_THICKNESS = 2
RED = (255,0,0)

class Camera:

    def __init__(self,speed):
       self.ROAD_MASK = cv.imread(r"C:\Users\pedri\Downloads\RoadMask.jpg")[:,:,0]
       self.tracking = Tracker(60)
       self.exceedid = {}
       self.countf = 0
       self.exceed = 0
    
    def run(self,capture:cv.VideoCapture):
        backgtroundSubtractor =  cv.bgsegm.createBackgroundSubtractorMOG()
        #polígono da pista esquerda
        area1 = [(340, 423), (587, 446), (555, 576), (142, 543)]
        #polígono da pista direita
        area2 = [(697, 447), (921, 431), (1068, 531), (732, 576)]
        while(capture.isOpened()):
            self.countf += 1
            ret,frame = capture.read()
            
            if not ret:
                raise  Exception("Erro! Vídeo não pôde ser carregado apropriadamente.") 
            
            grayFrame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            blurredFrame = cv.GaussianBlur(grayFrame,(3,3),5)  # Testar outro filtros (se fizer diferença no resultado final)
            noBGFrame = backgtroundSubtractor.apply(blurredFrame) 
            
            np.bitwise_and(noBGFrame,self.ROAD_MASK,noBGFrame)
                
            kernelM = cv.getStructuringElement(cv.MORPH_ELLIPSE,(6,6))
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernelM,iterations=2)
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_OPEN,kernelM,iterations=3)
            
            contours, hierarchy = cv.findContours(noBGFrame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                
            detected = []
            for objectCoords in contours:
                area = cv.contourArea(objectCoords)
                #If its area is less than 1000, its probably not a vehicule.
                if area < 1000:
                    continue

                x,y,w,h = cv.boundingRect(objectCoords)
                #Pegar centro do objeto
                cx = (x + x + w) // 2
                cy = (y + y + h) // 2

                #desenha polígonos no vídeo
                for a in [area1, area2]:
                    cv.polylines(frame, [np.array(a, np.int32)], True, BOX_COLOR_OKAY,BOX_THICKNESS)
                
                #contorna o veiculo somente quando o centro dele cruza com o poligono
                inRoi = False
                testPoly = cv.pointPolygonTest(np.array(area1, np.int32), (cx,cy), False)
                testPoly2 = cv.pointPolygonTest(np.array(area2, np.int32), (cx,cy), False)
                if testPoly >= 0 or testPoly2 >= 0:
                    inRoi = True
                    
                #Vendo só os da pista direita.
                if (cy < LOW_POINT_RIGHT_POLY and cy > TOP_LINE_RIGHT) or (cy > HIGH_POINT_LEFT_POLY):
                    detected.append((x,y,w,h,inRoi))

            
            out = self.tracking.update(detected,self.countf)
            
            for i in range(len(out)):
                id,speed = out[i]
                
                if(id == -1 and speed == -1):
                    continue
                
                x,y,w,h,_ = detected[i]
                cx = (x + x + w) // 2
                cy = (y + y + h) // 2
                
                if self.tracking.overSpeed(speed):
                    box_color = BOX_COLOR_OVER
                    if self.exceedid.get(id) == None:
                        self.exceedid[id] = True
                        self.exceed += 1
                else:
                    box_color = BOX_COLOR_OKAY
            
                frame = cv.rectangle(frame,(x,y),(x+w,y+h),box_color,BOX_THICKNESS) 
                cv.putText(frame,str(id)+f" {speed:.2f} km/h",(x,y-15),cv.FONT_HERSHEY_PLAIN,1,(255,255,0),2)                  
                cv.circle(frame, (cx,cy),5,(255,255,255),BOX_THICKNESS)
                    
            cv.putText(frame, f'Vehicles: {self.tracking.getAmount()}', (450, 70), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            cv.putText(frame, f'Infractors: {self.exceed}', (40, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # cv.line(frame, (0,TOP_LINE_RIGHT), (1200,TOP_LINE_RIGHT), (0,0,255), 2)
            # cv.line(frame, (0,BOTTOM_LINE_RIGHT), (1200,BOTTOM_LINE_RIGHT), (0,0,255), 2)
            
            # cv.line(frame, (MIDDLE_RAY,0), (MIDDLE_RAY,700), (255,0,255), 2)
            # if(self.countf == 215):
            #     cv.imwrite("final.jpeg",frame)
            cv.imshow("Video:",frame)

            if cv.waitKey(1) == ord('q'):   
                break
            
        capture.release()
        cv.destroyAllWindows()
        
video = cv.VideoCapture(r"C:\Users\pedri\Downloads\cars_video.mp4")
            
cam = Camera(60)
cam.run(video)