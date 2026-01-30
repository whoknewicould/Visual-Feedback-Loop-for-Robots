#!/usr/bin/env python3
"""
Entry point for the Visual Feedback Loop.
  Camera → Vision → Decision → Control → (Simulated) Motion → Camera
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from control.controller import Controller
from loop.feedback_loop import FeedbackLoop
from vision.detector import Detector
from vision.tracker import SimpleTracker


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Visual Feedback Loop: perception → decision → control (simulated)."
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Camera index (e.g. 0) or path to video file.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable OpenCV window (e.g. for headless / Docker).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="YOLOv8 model (e.g. yolov8n.pt, yolov8s.pt).",
    )
    parser.add_argument(
        "--center-margin",
        type=float,
        default=0.15,
        help="Normalized band around center for 'centered' (default 0.15).",
    )
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    detector = Detector(model_name=args.model)
    tracker = SimpleTracker()
    controller = Controller(center_margin=args.center_margin)
    loop = FeedbackLoop(detector, tracker, controller)

    loop.run(source=source, display=not args.no_display)
    return 0


if __name__ == "__main__":
    sys.exit(main())
