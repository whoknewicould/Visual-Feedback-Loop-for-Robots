<<<<<<< HEAD
# Visual Feedback Loop for Robots

A **real-time Visual Feedback Loop** where camera perception continuously influences robot actions, forming a closed-loop **perception–action** cycle. The robot (or simulated robot) perceives the environment via camera input, analyzes it in real time, and adjusts its actions based on visual feedback.

---

## Closed-Loop Explanation

A **closed loop** means the system’s output (motion / control) is fed back into its input (camera view). The flow is:

1. **Camera** captures the current scene.
2. **Vision** (YOLOv8 + optional tracker) detects objects and target position.
3. **Decision** (rule-based controller) decides what to do from that state.
4. **Control** produces linear/angular commands (simulated here).
5. **Motion** would move the robot; in simulation we only visualize the commands.
6. The scene changes (or the robot moves), and the next frame goes to **Camera** again.

So: **Camera → Vision → Decision → Control → Motion → Camera**. Each cycle uses the latest image to correct behavior, unlike an open-loop system that runs a fixed plan without re-checking the world.

---

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                  VISUAL FEEDBACK LOOP                     │
                    └─────────────────────────────────────────────────────────┘

     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
     │  CAMERA  │────▶│  VISION  │────▶│ DECISION │────▶│ CONTROL  │────▶│  MOTION  │
     │ (webcam  │     │ YOLOv8   │     │ (rules)  │     │ linear/  │     │(simulated│
     │ /video)  │     │ tracker  │     │          │     │ angular  │     │ or robot)│
     └──────────┘     └──────────┘     └──────────┘     └──────────┘     └────┬─────┘
          ▲                │                  │                  │             │
          │                │                  │                  │             │
          └────────────────┴──────────────────┴──────────────────┴─────────────┘
                                    FEEDBACK (updated scene)
```

- **Vision**: object detection (YOLOv8) + optional tracking (OpenCV / MediaPipe).
- **Decision**: rule-based (object left → rotate left, centered → forward, lost → search).
- **Control**: outputs `(linear, angular)`; in this repo they are simulated and visualized.

---

## Real-World Robotics Relevance

- **Servoing**: Keeping a target in the image center (e.g. person following, object tracking) is visual servoing; this loop is a simple form of it.
- **Safety**: Continuous perception lets the robot react to changes (obstacles, people) instead of blindly executing a path.
- **Adaptability**: New frames constantly update the decision, so the system adapts to motion and lighting without retraining.
- **Foundation for ROS**: The same loop (camera → vision → decision → control) maps directly to ROS nodes (camera driver, perception node, controller node, cmd_vel), with topics replacing in-process calls.

---

## How Latency Affects Feedback Loops

- **End-to-end latency** = camera capture + vision inference + decision + control + actuation.
- **Too high latency**: By the time the robot acts, the world has changed; the system can overshoot, oscillate, or become unstable.
- **Mitigation**: Use faster models (e.g. YOLOv8n), lower resolution, and higher frame rate where possible; in ROS, use async pipelines and tuned control gains.
- This project uses CPU-only YOLOv8; for lower latency on real robots, GPU or smaller models are recommended.

---

## Future ROS Integration Notes

- **Topics**: Publish images from a camera driver; subscribe in a perception node that runs YOLOv8/tracker and publishes target pose or bounding boxes; controller node subscribes and publishes `geometry_msgs/Twist` (cmd_vel).
- **Nodes**: `vision_node` (detector + tracker), `controller_node` (rule-based from vision state), optional `feedback_loop` node that wires them.
- **Gazebo**: Use a camera plugin (e.g. `libgazebo_ros_camera.so`) to publish image topics; the same perception and control code can subscribe to `/camera/image_raw` instead of a webcam.
- **Simulation**: Replace `ControlSignal` with `cmd_vel` publishing; motion is then simulated in Gazebo or another simulator.

---

## Project Structure

```
visual_feedback_loop/
├── docker/
│   └── Dockerfile
├── venv/
├── vision/
│   ├── detector.py    # YOLOv8 (pretrained)
│   └── tracker.py     # OpenCV / MediaPipe (optional)
├── control/
│   └── controller.py  # Rule-based: left/center/right/search
├── loop/
│   └── feedback_loop.py
├── run.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup

### Virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
# One-time: install dependencies (YOLOv8, OpenCV, etc.)
pip install -r requirements.txt

# With webcam (quit with 'q')
python run.py
```

**Quick test without camera** (one step on a synthetic frame):

```bash
python test_run.py
```

- **Webcam**: default source is `0`. Quit with `q` in the OpenCV window.
- **Video file**: `python run.py --source /path/to/video.mp4`
- **Headless / no display**: `python run.py --no-display` (e.g. in Docker or SSH).

### Docker

- **Image**: CPU-only, base `python:3.10-slim`. Build from project root:
  - `docker build -t vfl -f docker/Dockerfile .`
- **Webcam**: Optional. To use a webcam in the container, run with device access and (if you want a window) display:
  - `docker run --device=/dev/video0 -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix vfl`
- **Limitation**: In many CI/cloud environments there is no camera or display; use `--no-display` and a video file as `--source` for testing.

---

## Control Rules (Rule-Based, No RL)

| Condition        | Action        | Output (simulated)   |
|-----------------|---------------|----------------------|
| Object left     | Rotate left   | angular &gt; 0       |
| Object right    | Rotate right  | angular &lt; 0       |
| Object centered | Move forward  | linear &gt; 0        |
| Object lost     | Search mode   | slow rotation        |

Center band and speeds are configurable in `control/controller.py` and via `run.py --center-margin`.

---

## License

See repository license file.
=======
# Visual-Feedback-Loop-for-Robots
>>>>>>> c92d07c0ea4b7267286bcec04eb2c4fe01863969
