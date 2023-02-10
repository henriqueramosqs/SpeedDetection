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

                x,y,w,h = cv.boundingRect(objectCoords)
                #Pegar centro do objeto
                cx = (x + x + w) // 2
                cy = (y + y + h) // 2
                
                #contorna o veiculo somente quando o centro dele cruza com o poligono
                testPoly = cv.pointPolygonTest(np.array(area1, np.int32), (cx,cy), False)
                testPoly2 = cv.pointPolygonTest(np.array(area2, np.int32), (cx,cy), False)
                if testPoly >= 0 or testPoly2 >= 0:
                    frame = cv.rectangle(frame,(x,y),(x+w,y+h),BOX_COLOR,BOX_THICKNESS)                   
                    cv.circle(frame, (cx,cy),5,BOX_COLOR,BOX_THICKNESS)
                    
            #polígono da pista esquerda
            area1 = [(340, 423), (587, 446), (555, 576), (142, 543)]
            #polígono da pista direita
            area2 = [(697, 447), (921, 431), (1068, 531), (732, 576)]
            #desenha polígonos no vídeo
            for a in [area1, area2]:
                cv.polylines(frame, [np.array(a, np.int32)], True, BOX_COLOR,BOX_THICKNESS)

            #cv.putText(frame, f'Frame: {counter}', (450, 70), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv.imshow("Video:",frame)

            if cv.waitKey(1) == ord('q'):   
                break


        capture.release()
        cv.destroyAllWindows()



video = cv.VideoCapture("video.mp4")

            
cam = Camera(2)
cam.run(video)