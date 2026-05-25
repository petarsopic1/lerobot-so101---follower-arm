# 🤖 6-DOF Robotic Arm Control System (SCADA & Multi-Axis Sync)

An end-to-end industrial-grade automation solution for kinesthetic teaching, real-time trajectory logging, and synchronous multi-axis execution on a 6-Degree-of-Freedom (6-DOF) robotic arm. Powered by **STS3215 smart serial bus servos** and managed via a headless **Raspberry Pi Architecture**, this repository bridges low-level hardware registers with an intuitive, web-based SCADA interface built entirely on **Node-RED**.

---

## 🛠️ System Architecture & Data Flow

The system bypasses legacy terminal-based execution by creating an asynchronous, file-based control loop between the frontend web services and the backend Python execution engines.

[ Kinesthetic Teaching ] ---> Releases Torque ---> Manual Hand-Guiding
|
[ Save Point Button ]    <--- Snatch Positions <--- [ uslikaj_tocku.py ]
|
Filters Raw Data (UI logs only)
|
[ Run Robot Button ]     ---> Compiles Array + Sliders ---> [ plan_gibanja.json ]
|
[ pokreni_robot.py ]     <--- Parses Payload & Locks Registers <---+
|
[ write_synchronous() ]  ---> Unified Multi-Axis Frame ---> 6x STS3215 Servos

### 1. Kinesthetic Teaching & Zero-G Mode
When the operator triggers the "Torque Off" sequence (`ugasi_torq.py`), the system communicates over the half-duplex UART bus to release the magnetic holding tension of all 6 actuators. This shifts the robot into a passive state, enabling human operators to manually guide the arm through physical trajectories (kinesthetic teaching).

### 2. Multi-Coordinate Real-Time Capture
Upon triggering a "Save Point", Node-RED invokes `uslikaj_tocku.py`. The script polls all 6 servo registers synchronously. To optimize UI readability and prevent data fatigue, a custom JavaScript pipeline filters the raw 6-axis array streams in the background, updating the SCADA panel with a sanitized, high-level event log (*"Point X successfully recorded!"*) while caching the raw joint steps in the volatile flow memory.

### 3. Mission Planner & JSON Payload Serialization
When the "Run Robot" pipeline is executed, Node-RED dynamically samples the current positions of the UI configuration sliders (Speed and Acceleration) and packs them alongside the recorded multi-coordinate sequence array into a unified mission manifest stored at `/home/pi/robot/plan_gibanja.json`.

---

## ⚙️ Core Technical Mechanisms

### 🔌 Automated Failover Driver (Hot-Plugging)
The underlying communication layer utilizes an intelligent serial bus mapping framework within the `STS3215` driver class. In industrial environments, USB serial ports often reset or switch paths upon reboot. The driver automatically scans the system's active device tree for Linux abstract control mechanisms:
* Primary Target: `/dev/ttyACM0`
* Secondary Failover: `/dev/ttyACM1`

This layout guarantees continuous runtime operation without requiring manual port configuration or script rewrites if hardware peripherals are hot-plugged.

### ⏱️ Synchronous Motion Profiling & Timing Math
Traditional serial commands update actuators sequentially, introducing noticeable lag between the movement of Joint 1 and Joint 6. This project overcomes this bottleneck using the native `write_synchronous()` bus protocol. All target positions, acceleration ramps, and velocity limits are concatenated into a single broadcast packet sent simultaneously across the bus.

To ensure the arm does not attempt to execute a new point before the physical servos finish their current travel profile, the execution engine (`pokreni_robot.py`) implements dynamic timing math. It computes the absolute travel delta for each joint and isolates the maximum angular distance:

$$\Delta P_{max} = \max_{i=1..6} |Position_{new, i} - Position_{old, i}|$$

The calculated execution delay is then dynamically scaled based on the operator's real-time speed configuration ($V$), complemented by a safety margin ($\delta$):

$$t_{delay} = \left( \frac{\Delta P_{max}}{V} \right) + 0.15\text{s}$$

This prevents structural jerks, eliminates collision paths, and ensures perfectly smooth, synchronized paths regardless of the distance variance between separate joints.

---

## 📂 File Directory Structure

* **`uslikaj_tocku.py`**: Queries current absolute position registers for IDs 1 through 6 over the serial bus and outputs comma-separated values.
* **`ugasi_torq.py`**: Broadcasts a register write to un-torque all active joints, allowing hand-guided positioning.
* **`pokreni_robot.py`**: The core execution engine. Parses the JSON mission plan, computes motion profiling delays, locks servo torques, and fires the unified `write_synchronous` packets.
* **`node_red_flow.json`**: The complete exported SCADA dashboard configuration, including touch targets, CSS style rules, variable caching nodes, and JSON serialization logic.
* **`.gitignore`**: Excludes `.venv/` runtime binaries, `__pycache__` systems, and ephemeral `plan_gibanja.json` maps from polluting the repository.

---

## 🚀 Installation & Deployment

### Prerequisites
* Raspberry Pi 4 / 5 running Raspberry Pi OS (Debian-based)
* Python 3.10+ with `venv`
* Node-RED installed and running as a systemd service

### 1. Clone & Set Up Python Environment
```bash
cd ~
git clone [https://github.com/petarsopic1/lerobot-so101---follower-arm.git](https://github.com/petarsopic1/lerobot-so101---follower-arm.git) robot
cd robot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Deploy the SCADA Dashboard
Open the file node_red_flow.json in a text editor and copy its entire content.

Open your browser and navigate to your local Node-RED instance (typically http://<your-pi-ip>:1880).

Click the Menu button (top right corner) -> Import.

Paste the copied JSON payload into the text area and select Import to New Flow.

Click Deploy in the top right corner.

3. Hardware Hookup
Connect your STS3215 serial bus smart servos through your dedicated hardware interface adapter into any available USB port on the Raspberry Pi. The driver handles port allocation automatically.

🛠️ Tech Stack
Hardware Compute: Raspberry Pi (Linux ARM architecture)

Actuation: 6x STS3215 Smart Serial Bus Servos (Half-Duplex UART Communication)

Backend Runtime: Python 3 (Virtual Environment Isolations)

Frontend UI / Middleware: Node-RED Engine (Asynchronous JavaScript Processing)