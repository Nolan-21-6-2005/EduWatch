import time

class AlertManager:
    def __init__(self, cooldown = 5):
        self.cooldown = cooldown
        self.history = []
        self.last_detect_time = {}

    def should_alert(self):
        return (time.time() - self.last_alert_time) > self.cooldown

    def send_alert(self, label, confidence):
        if self.should_alert():
            msg = f"Phát hiện {label} với độ tin cậy {confidence:.2f}"
            self.last_detect_time = time.time()
            self.history.append({"time": self.last_detect_time, "msg": msg})
            return True
        return False
