# Dance Dance Revolution - Embedded Systems Capstone Final Project

This project is the final assignment for the Embedded Systems course.  
We built a **foldable dance machine** 🎵💃🕺 that combines multiple sensors, actuators, and software modules to create a highly interactive game system.

---

## 📌 Motivation
1. Build a project with a high level of interactivity
2. Apply as many devices taught in class as possible, while also learning additional tools
3. A commercial DDR machine is expensive and too large to place at home — so we made our own foldable version

---

## 🛠️ Hardware
- WS2812 RGB LED Strip  
- Piezo Element  
- Microphone  
- Speaker  
- Camera  
- MCP3008 (ADC)  

---

## 💻 Software
- **LED Control**: `rpi_ws281x` (Python)  
- **Piezo Element**: signal converted via MCP3008, read through SPI  
- **Camera & Pose Detection**: `picamera2` + `mediapipe`  
- **Speech Recognition**: `speech_recognition`  
- **Synchronized Operation**: `subprocess` + `asyncio`  
- **GUI**: `tkinter`  

---

## 🔧 Challenges & Solutions
- **Unstable Piezo threshold** → Run calibration before each game  
- **LED timing vs. Piezo detection mismatch** → Adjust LED display delay by -0.5 sec  
- **Camera capture too slow** → Replaced built-in command with `picamera2`  
- **Hardware instability** → Frequent replacements and maintenance  

---

## 📊 Flow Chart
(Add the system flow chart image here if available)

---

## 🎮 Demo Videos
- **Single-player mode**: https://youtu.be/rWTyGv45E3o  
- **Two-player mode (high difficulty, one uses hands, one uses feet)**: https://youtu.be/2yeM9ls6854  

---

## ⚙️ Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/yiocean/embedded_system_final_project.git
cd embedded_system_final_project
````

### 2. Set up Python environment

It is recommended to use Python 3.9+ and a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the project

```bash
python DDR_game_ui.py
```

### 5. Calibration

Before starting the game, follow the on-screen instructions to calibrate the **Piezo elements** for accurate threshold detection.
