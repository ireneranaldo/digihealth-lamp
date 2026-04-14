import cv2
from typing import Dict, Any
from .base import BaseSensor
from ..logger import logger


class PeopleCounterSensor(BaseSensor):
    """People counting sensor using YOLOv8 and RTSP camera."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rtsp_url = config.get('rtsp_url')
        self.model_path = config.get('model_path', 'yolov8n.pt')
        self.frame_width = config.get('frame_width', 640)
        self.frame_height = config.get('frame_height', 480)
        self.show_video = config.get('show_video', False)
        self.frame_interval = config.get('frame_interval', 2)  # Secondi tra i frame visualizzati
        self.model = None
        self.cap = None
        self.last_frame_time = 0
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"Loaded YOLO model: {self.model_path}")
        except Exception as e:
            self.logger.error(f"Unable to load YOLO model: {e}")
            self.model = None

    def is_available(self) -> bool:
        if not self.rtsp_url:
            self.logger.error("People counter RTSP URL is missing in configuration")
            return False

        if self.model is None:
            self._load_model()
            if self.model is None:
                return False

        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            if not cap.isOpened():
                self.logger.error("Unable to open RTSP stream for people counter")
                return False
            cap.release()
            return True
        except Exception as e:
            self.logger.error(f"People counter camera not available: {e}")
            return False

    def read(self) -> Dict[str, Any]:
        if self.model is None:
            self._load_model()
            if self.model is None:
                return {}

        if not self.rtsp_url:
            return {}

        try:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.rtsp_url)

            if not self.cap.isOpened():
                self.logger.error("Unable to open RTSP stream during people count read")
                return {}

            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.logger.error("Unable to read frame from RTSP stream")
                return {}

            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            results = self.model(frame, verbose=False)
            
            person_count = 0
            person_boxes = []
            
            # Conta persone e raccoglie bounding boxes
            for box in results[0].boxes:
                if int(box.cls) == 0:  # Classe YOLO 0 = person
                    person_count += 1
                    person_boxes.append(box)
            
            # Visualizza il video se abilitato
            if self.show_video:
                try:
                    import time
                    current_time = time.time()
                    
                    # Visualizza il frame ogni N secondi
                    if current_time - self.last_frame_time >= self.frame_interval:
                        self.last_frame_time = current_time
                        
                        # Disegna i bounding boxes
                        for box in person_boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Scrivi il conteggio delle persone sul frame
                        cv2.putText(
                            frame,
                            f"People: {person_count}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )
                        
                        cv2.imshow("YOLOv8 People Counter", frame)
                        
                        # Premi 'q' per uscire dal preview
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            self.show_video = False
                except Exception as e:
                    self.logger.warning(f"Unable to display video: {e} (headless system?)")

            return {"person_count": int(person_count)}
        except Exception as e:
            self.logger.error(f"Error reading people counter sensor: {e}")
            return {}
