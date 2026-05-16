import time
from ultralytics import YOLO

class Detector:
    def __init__(self, AI_PATH):
        self.model = YOLO(AI_PATH)
        self._is_active = True

    def detect_object(self, frame):
        results = self.model(frame, imgsz=320)
        return results
        
    def is_active(self):
        return self._is_active
    
    def activate(self):
        """Hàm bật AI"""
        self._is_active = True

    def deactivate(self):
        """Hàm tắt AI"""
        self._is_active = False

