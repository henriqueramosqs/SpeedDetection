import cv2 as cv
import numpy as np
from tracker import *

BOX_COLOR = (0,255,0)
BOX_THICKNESS = 2
RED = (255,0,0)

class Camera:
    #  Infomrações uteis a coloca no init
    #  1) angulação da câmera com a pista 
    #  2) Máscara para remover "o que não é pista" (X)
    #  3) Largura e comprimento máx dos carros  (X)
    #  4) Fazer delimitadores mudarem de cor quando algo passa
    def __init__(self,roadQtd:int):
       #self.ROAD_MASK = cv.imread("RoadMask.jpg")[:,:,0]
       self.countf = 0
       self.roadDelimiter = 398
       self.queues=[[]for i in range(roadQtd)]
       self.tracking = Tracker()
       
    def getRoad(self,bottomLeftPos:int):
        if(bottomLeftPos>self.roadDelimiter):
            return 1
        else:
            return 0
    
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
            
            #np.bitwise_and(noBGFrame,self.ROAD_MASK,noBGFrame)
            
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(8,8))
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel,iterations=2)
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_OPEN,kernel,iterations=2)

            contours, hierarchy = cv.findContours(noBGFrame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            if(len(contours) == 0):
                self.tracking.clean()
                
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
                    cv.polylines(frame, [np.array(a, np.int32)], True, BOX_COLOR,BOX_THICKNESS)
                
                #contorna o veiculo somente quando o centro dele cruza com o poligono
                inRoi = False
                testPoly = cv.pointPolygonTest(np.array(area1, np.int32), (cx,cy), False)
                testPoly2 = cv.pointPolygonTest(np.array(area2, np.int32), (cx,cy), False)
                if testPoly >= 0 or testPoly2 >= 0:
                    inRoi = True
                    
                #Vendo só os da pista direita.
                if (cx > MIDDLE_RAY and cy < LOW_POINT_RIGHT_POLY and cy > TOP_LINE_RIGHT):
                    detected.append((x,y,w,h,inRoi))

            
            out = self.tracking.update(detected,self.countf)
            
            for i in range(len(out)):
                id,speed = out[i]
                
                if(id == -1 and speed == -1):
                    continue
                
                x,y,w,h,_ = detected[i]
                cx = (x + x + w) // 2
                cy = (y + y + h) // 2
                frame = cv.rectangle(frame,(x,y),(x+w,y+h),BOX_COLOR,BOX_THICKNESS) 
                cv.putText(frame,str(id)+f" {speed:.2f} km/h",(x,y-15),cv.FONT_HERSHEY_PLAIN,1,(255,255,0),2)                  
                cv.circle(frame, (cx,cy),5,BOX_COLOR,BOX_THICKNESS)
                    
            cv.putText(frame, f'Vehicles: {self.tracking.getAmount()}', (450, 70), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv.circle(frame, (350,600),17,BOX_COLOR,BOX_THICKNESS)
            cv.line(frame, (0,TOP_LINE_RIGHT), (1200,TOP_LINE_RIGHT), (0,0,255), 2)
            cv.line(frame, (0,BOTTOM_LINE_RIGHT), (1200,BOTTOM_LINE_RIGHT), (0,0,255), 2)
            
            # cv.line(frame, (MIDDLE_RAY,0), (MIDDLE_RAY,700), (255,0,255), 2)
            cv.imshow("Video:",frame)

            if cv.waitKey(1) == ord('q'):   
                break
            
        capture.release()
        cv.destroyAllWindows()
        
video = cv.VideoCapture(r"C:\Users\pedri\OneDrive\Área de Trabalho\SEMESTRE_7\INTRO_AO_PROC_DE_IMAGENS\TRAB_2\video.mp4")
            
cam = Camera(2)
cam.run(video)