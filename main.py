import cv2 as cv

class Camera:
    #  Infomrações uteis a coloca no init
    #  1) angulação da câmera com a pista
    #  2) Máscara para remover "o que não é pista"
    #  3) Largura e comprimento máx dos carros 

    def run(self,capture:cv.VideoCapture):
        backgtroundSubtractor =  cv.bgsegm.createBackgroundSubtractorMOG()
        
        while(capture.isOpened()):
            ret,frame = capture.read()

            if not ret:
                raise  Exception("Erro! Vídeo não pôde ser carregado apropriadamente.") 

            grayFrame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            blurredFrame = cv.GaussianBlur(frame,(3,3),5)  # Testar outro filtros (se fizer diferença no resultado final)
            noBGFrame = backgtroundSubtractor.apply(blurredFrame) 

            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(8,8))
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel) # Vale a penna fazer outro fechamento?
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernel) 

            bounding, img = cv.findContours(noBGFrame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # Testar outros retrival modes

            cv.imshow("nbg",noBGFrame)
            cv.waitKey(100)

            if cv.waitKey(1) == ord('q'):   
                break

        capture.release()
        cv.destroyAllWindows()



video = cv.VideoCapture("video.mp4")

            
cam = Camera()
cam.run(video)