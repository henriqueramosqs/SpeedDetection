import cv2 as cv
import numpy as np

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
       self.ROAD_MASK = cv.imread("RoadMask.jpg")[:,:,0]
       self.roadDelimiter = 398
       self.queues=[[]for i in range(roadQtd)]

    def getRoad(self,bottomLeftPos:int):
        if(bottomLeftPos>self.roadDelimiter):
            return 1
        else:
            return 0
    

    def run(self,capture:cv.VideoCapture):
        backgtroundSubtractor =  cv.bgsegm.createBackgroundSubtractorMOG()
        counter=0
        while(capture.isOpened()):
            counter+=1
            ret,frame = capture.read()
            print(frame.shape)

            if not ret:
                raise  Exception("Erro! Vídeo não pôde ser carregado apropriadamente.") 

            grayFrame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            blurredFrame = cv.GaussianBlur(grayFrame,(3,3),5)  # Testar outro filtros (se fizer diferença no resultado final)
            noBGFrame = backgtroundSubtractor.apply(blurredFrame) 
            np.bitwise_and(noBGFrame,self.ROAD_MASK,noBGFrame)
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(8,8))
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel) # Vale a penna fazer outro fechamento?
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel) 

            contours, hierarchy = cv.findContours(noBGFrame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) # Testar outros retrival modes

            for objectCoords in contours:
                area = cv.contourArea(objectCoords)
                if area > 1000:
                    x,y,w,h = cv.boundingRect(objectCoords)
                    frame = cv.rectangle(frame,(x,y),(x+w,y+h),BOX_COLOR,BOX_THICKNESS)

            cv.line(frame, (0, 600), (0, 800), RED, 3)
            cv.line(frame, (500, 0), (700, 0), RED, 3)    

            cv.putText(frame, f'Frame: {counter}', (450, 70), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv.imshow("Video:",frame)

            if cv.waitKey(1) == ord('q'):   
                break


        capture.release()
        cv.destroyAllWindows()



video = cv.VideoCapture("video.mp4")

            
cam = Camera(2)
cam.run(video)