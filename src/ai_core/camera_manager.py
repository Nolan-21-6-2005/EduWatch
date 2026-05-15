import cv2

class CameraManager:
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
    
    def read_frame(self):
        return self.cap.read()
    
    def disconnect(self):
        self.cap.release()
        
