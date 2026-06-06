import cv2
import numpy as np


latest_detections = []
last_detect_time = {}
is_running = True
is_active = True

COOLDOWN = 5

# Màu xám tối (#2b2b2b)
placeholder_frame = np.ones((480, 640, 3), dtype=np.uint8) * 43 
cv2.putText(placeholder_frame, "CAMERA IS OFF", (160, 250), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2, cv2.LINE_AA)
            

