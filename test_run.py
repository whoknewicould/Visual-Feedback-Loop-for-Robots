#!/usr/bin/env python3
"""Quick test: one feedback-loop step with a synthetic frame (no camera)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from vision.detector import Detector
from vision.tracker import SimpleTracker
from control.controller import Controller
from loop.feedback_loop import FeedbackLoop

def main():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (128, 128, 128)
    detector = Detector(model_name="yolov8n.pt")
    tracker = SimpleTracker()
    controller = Controller()
    loop = FeedbackLoop(detector, tracker, controller)
    annotated, control, state = loop.step(frame)
    print("OK: one step completed.")
    print(f"  Control: {control.mode} L={control.linear:.2f} A={control.angular:.2f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
