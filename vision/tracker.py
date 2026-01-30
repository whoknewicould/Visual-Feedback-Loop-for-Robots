"""
Optional pose / tracking utilities using OpenCV and MediaPipe (pretrained only).
Used for tracking a region or pose when needed by the feedback loop.
"""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np

# MediaPipe optional
try:
    import mediapipe as mp
except ImportError:
    mp = None


def center_of_bbox(xyxy: np.ndarray) -> tuple[float, float]:
    """Return (cx, cy) center of bbox [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = xyxy
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def bbox_in_frame_normalized(
    xyxy: np.ndarray,
    width: int,
    height: int,
) -> tuple[float, float]:
    """
    Return (cx_norm, cy_norm) in [0, 1] for frame dimensions.
    Useful for control: 0.5 = center.
    """
    cx, cy = center_of_bbox(xyxy)
    return (cx / width if width else 0.5, cy / height if height else 0.5)


class PoseTracker:
    """MediaPipe pose estimation (optional). Exposes landmark positions for control."""

    def __init__(self, min_detection_confidence: float = 0.5) -> None:
        if mp is None:
            raise ImportError("Install mediapipe: pip install mediapipe")
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5,
        )

    def process(self, frame: np.ndarray) -> list[tuple[float, float]] | None:
        """
        Run pose on RGB frame. Returns list of (x, y) normalized [0,1] or None.
        Index by mp.solutions.pose.PoseLandmark (e.g. NOSE = 0).
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        if not results.pose_landmarks:
            return None
        return [
            (lm.x, lm.y)
            for lm in results.pose_landmarks.landmark
        ]

    def close(self) -> None:
        self.pose.close()


class SimpleTracker:
    """
    OpenCV-based centroid tracker for a single ROI or detection.
    Tracks 'lost' vs 'found' for search-mode logic.
    """

    def __init__(self) -> None:
        self.last_center: tuple[float, float] | None = None
        self.lost_frames = 0
        self.lost_threshold = 10  # consider lost after N frames without detection

    def update(
        self,
        detections: list[dict[str, Any]],
        frame_width: int,
        frame_height: int,
    ) -> dict[str, Any]:
        """
        Update state from current detections. Prefer first detection as 'target'.
        Returns {
            "found": bool,
            "cx_norm": float in [0,1],
            "cy_norm": float in [0,1],
            "bbox_xyxy": optional,
        }.
        """
        if not detections:
            self.lost_frames += 1
            if self.lost_frames >= self.lost_threshold:
                self.last_center = None
            return {
                "found": self.lost_frames < self.lost_threshold and self.last_center is not None,
                "cx_norm": 0.5 if self.last_center is None else self.last_center[0],
                "cy_norm": 0.5 if self.last_center is None else self.last_center[1],
                "bbox_xyxy": None,
            }
        d = detections[0]
        xyxy = d["bbox_xyxy"]
        cx_norm, cy_norm = bbox_in_frame_normalized(xyxy, frame_width, frame_height)
        self.last_center = (cx_norm, cy_norm)
        self.lost_frames = 0
        return {
            "found": True,
            "cx_norm": cx_norm,
            "cy_norm": cy_norm,
            "bbox_xyxy": xyxy,
        }
