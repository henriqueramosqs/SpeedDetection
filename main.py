import cv2 as cv
import numpy as np

BOX_COLOR = (0,255,0)
BOX_THICKNESS = 2

class Camera:

    def __init__(self):
       self.ROAD_MASK = cv.imread("RoadMask.jpg")[:,:,0]
    #  Infomrações uteis a coloca no init
    #  1) angulação da câmera com a pista
    #  2) Máscara para remover "o que não é pista"
    #  3) Largura e comprimento máx dos carros 

    def run(self,capture:cv.VideoCapture):
        backgtroundSubtractor =  cv.bgsegm.createBackgroundSubtractorMOG()
        counter=0
        while(capture.isOpened()):
            counter+=1
            ret,frame = capture.read()

            if not ret:
                raise  Exception("Erro! Vídeo não pôde ser carregado apropriadamente.") 

            grayFrame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            blurredFrame = cv.GaussianBlur(grayFrame,(3,3),5)  # Testar outro filtros (se fizer diferença no resultado final)
            noBGFrame = backgtroundSubtractor.apply(blurredFrame) 
            np.bitwise_and(noBGFrame,self.ROAD_MASK,noBGFrame)
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(8,8))
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel) # Vale a penna fazer outro fechamento?
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel) 

            contours, hierarchy = cv.findContours(noBGFrame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # Testar outros retrival modes

            for objectCoords in contours:
                # Vale à pena validar tamanhos dos contornos?
                area = cv.contourArea(objectCoords)
                if area > 1000:
                    x,y,w,h = cv.boundingRect(objectCoords)
                    frame = cv.rectangle(frame,(x,y),(x+w,y+h),BOX_COLOR,BOX_THICKNESS)
            
            cv.imshow("Video:",frame)

            if(counter==20):
                cv.imwrite("VAI.jpg",frame)
            if cv.waitKey(1) == ord('q'):   
                break


        capture.release()
        cv.destroyAllWindows()



video = cv.VideoCapture("video.mp4")

            
cam = Camera()
cam.run(video)