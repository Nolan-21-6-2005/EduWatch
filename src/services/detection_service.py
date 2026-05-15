from src.ai_core.camera_manager import CameraManager
from src.ai_core.detector import Detector
from cv2
from src.utils.model import AI_PATH

camera_manager = CameraManager(0)
detector = Detector(AI_PATH)
alert_handler = AlertManager(cooldown=60)

def display(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()

    return (
        b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' +
        frame_bytes +
        b'\r\n'
    )

def process_alert(results, alert_manager):
    for r in results:
        if len(r.boxes) > 0:
            label = r.names[int(r.boxes[0].cls)]
            conf = float(r.boxes[0].conf)
            # Gọi class manager để check cooldown và gửi
            alert_manager.send_alert(label, conf)

def gen_frames():
    try:
        while True:
            # Doc camera
            success, frame = camera_manager.read_frame()

            if not success: break

            if detector.is_active():
                results = detector.detect_object(frame)
                
                process_alert(results, alert_manager)
                
                # Ve khung len hinh
                output_frame = results[0].plot()
                yield display(output_frame)
            else
                output_frame = frame
                yield display(output_frame)
    except Exception as e:
        print(f"Error: {e}")

