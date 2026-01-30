"""
YOLOv8-based object detector (pretrained only).
Provides bounding boxes and class labels for feedback-loop decisions.
"""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


class Detector:
    """YOLOv8 detector wrapper for real-time object detection."""

    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
    ) -> None:
        if YOLO is None:
            raise ImportError("Install ultralytics: pip install ultralytics")
        self.model = YOLO(model_name)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    def detect(
        self,
        frame: np.ndarray,
        classes: list[int] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Run detection on a BGR frame.
        Returns list of detections: [{bbox_xyxy, class_id, class_name, conf}, ...].
        """
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=classes,
            verbose=False,
        )
        out: list[dict[str, Any]] = []
        if not results:
            return out
        r = results[0]
        if r.boxes is None:
            return out
        boxes = r.boxes
        for i in range(len(boxes)):
            xyxy = boxes.xyxy[i].cpu().numpy()
            conf = float(boxes.conf[i].cpu().numpy())
            cls_id = int(boxes.cls[i].cpu().numpy())
            cls_name = r.names.get(cls_id, str(cls_id))
            out.append({
                "bbox_xyxy": xyxy,
                "class_id": cls_id,
                "class_name": cls_name,
                "conf": conf,
            })
        return out

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: list[dict[str, Any]],
        color: tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """Draw bounding boxes and labels on frame (in-place style; returns frame)."""
        out = frame.copy()
        for d in detections:
            x1, y1, x2, y2 = d["bbox_xyxy"].astype(int)
            label = f"{d['class_name']} {d['conf']:.2f}"
            cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(out, (x1, y1 - th - 4), (x1 + tw, y1), color, -1)
            cv2.putText(
                out, label, (x1, y1 - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1,
            )
        return out
