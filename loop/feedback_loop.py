"""
Closed-loop perception–action cycle:
  Camera → Vision → Decision → Control → (Simulated) Motion → Camera
"""

from __future__ import annotations

import time
from typing import Any, Callable

import cv2
import numpy as np

from control.controller import ControlSignal, Controller
from vision.detector import Detector
from vision.tracker import SimpleTracker


class FeedbackLoop:
    """
    Runs the visual feedback loop:
    - Capture frame from camera
    - Run detector (YOLOv8)
    - Update tracker state (target position / lost)
    - Compute control from controller
    - Optionally visualize and yield (frame, control, state)
    """

    def __init__(
        self,
        detector: Detector,
        tracker: SimpleTracker,
        controller: Controller,
        target_classes: list[int] | None = None,
    ) -> None:
        self.detector = detector
        self.tracker = tracker
        self.controller = controller
        self.target_classes = target_classes  # restrict detection; None = all

    def step(
        self,
        frame: np.ndarray,
    ) -> tuple[np.ndarray, ControlSignal, dict[str, Any]]:
        """
        One iteration: frame in → annotated frame out, control signal, state.
        """
        h, w = frame.shape[:2]
        detections = self.detector.detect(frame, classes=self.target_classes)
        tracker_state = self.tracker.update(detections, w, h)
        control = self.controller.update(tracker_state)
        annotated = self.detector.draw_detections(frame, detections)
        annotated = self._draw_feedback(annotated, tracker_state, control, w, h)
        state = {
            "detections": detections,
            "tracker_state": tracker_state,
            "control": control,
        }
        return annotated, control, state

    def _draw_feedback(
        self,
        frame: np.ndarray,
        tracker_state: dict[str, Any],
        control: ControlSignal,
        width: int,
        height: int,
    ) -> np.ndarray:
        """Overlay center band, target position, and control text."""
        out = frame.copy()
        cx = int(tracker_state.get("cx_norm", 0.5) * width)
        cy = int(tracker_state.get("cy_norm", 0.5) * height)
        margin = int(0.15 * width)
        # Center band (green = good)
        cv2.rectangle(out, (width // 2 - margin, 0), (width // 2 + margin, height), (0, 200, 0), 1)
        # Target point
        color = (0, 255, 0) if tracker_state.get("found") else (0, 0, 255)
        cv2.circle(out, (cx, cy), 8, color, 2)
        # Control text
        text = f"{control.mode} L:{control.linear:.2f} A:{control.angular:.2f}"
        cv2.putText(out, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(out, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        return out

    def run(
        self,
        source: int | str = 0,
        display: bool = True,
        on_step: Callable[[np.ndarray, ControlSignal, dict], None] | None = None,
    ) -> None:
        """
        Run loop from camera (source=0) or video file.
        If display=True, show annotated window. on_step called each iteration.
        """
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {source}")
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                annotated, control, state = self.step(frame)
                if on_step:
                    on_step(annotated, control, state)
                if display:
                    cv2.imshow("Visual Feedback Loop", annotated)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()
