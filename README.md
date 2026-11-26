
# Nirvana Wheel

An interactive school exhibition project that connects colour recognition with the Buddhist Noble Eightfold Path.

Visitors rotate a physical eight-colour wheel. An ESP32-C3 connected to a TCS3200 colour sensor detects the selected colour and sends sensor readings to a Python application on a PC. The application identifies the colour, introduces its corresponding path, and plays its prerecorded audio description.

## Features

- Eight-colour wheel with colour recognition.
- TCS3200 colour sensor.
- ESP32-C3 microcontroller.
- Serial communication between ESP32 and PC.
- Python-based colour calibration and classification.
- Eight corresponding audio descriptions.
- Automatic audio playback when a new colour is detected.

## Colour Mapping

| Colour | Noble Eightfold Path | Audio File |
|---|---|---|
| Green | Right View | `view.mp3` |
| Blue | Right Intention | `intention.mp3` |
| Yellow | Right Speech | `speech.mp3` |
| Red | Right Action | `action.mp3` |
| Violet | Right Livelihood | `livelihood.mp3` |
| Purple | Right Concentration | `concentration.mp3` |
| Orange | Right Mindfulness | `mindfulness.mp3` |
| Brown | Right Effort | `effort.mp3` |

## Hardware

- ESP32-C3 DevKitM-1
- TCS3200 colour sensor module
- Eight-colour physical wheel
- USB cable
- PC or laptop

### TCS3200 Wiring

| TCS3200 Pin | ESP32-C3 GPIO |
|---|---|
| OUT | GPIO 0 |
| S0 | GPIO 1 |
| S1 | GPIO 4 |
| S2 | GPIO 5 |
| S3 | GPIO 6 |
| LED | GPIO 7 |
| VCC | 3.3V |
| GND | GND |

## Software Requirements

- Python 3.10 or newer
- PlatformIO
- Visual Studio Code (recommended)
- ESP32 Arduino framework

## Project Structure

```text
nirvana-wheel/
│
├── nirvana_wheel.py
├── nirvana_paths.py
├── tcs3200_test.py
├── colour_calibration.json
├── requirements.txt
├── .gitignore
├── README.md
│
├── audio/
│   ├── view.mp3
│   ├── intention.mp3
│   ├── speech.mp3
│   ├── action.mp3
│   ├── livelihood.mp3
│   ├── concentration.mp3
│   ├── mindfulness.mp3
│   └── effort.mp3
│
└── firmware/
    └── platformio.ini
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/nirvana-wheel.git
cd nirvana-wheel
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Calibration

1. Connect the ESP32-C3 to the PC.
2. Confirm the correct serial port in the Python scripts.
3. Run:

```bash
python tcs3200_test.py
```

4. Select calibration mode.
5. Place each of the eight colours under the sensor when prompted.
6. Save the resulting `colour_calibration.json`.

Keep the sensor distance, angle and lighting consistent during calibration and operation.

## Run the Wheel

```bash
python nirvana_wheel.py
```

The application reads sensor data, identifies stable colour readings and plays the matching audio description.

## Firmware

The ESP32-C3 firmware is developed using PlatformIO and the Arduino framework.

Sensor readings are transmitted over serial at 115200 baud.

## Notes

- Keep the sensor and wheel lighting conditions consistent.
- Recalibrate if the sensor position or lighting changes.
- The serial port configured in the Python scripts must match the connected ESP32.
- The calibration file is generated locally and should be kept with the project.

## Project Purpose

The Nirvana Wheel is designed to make the Buddhist Noble Eightfold Path interactive and accessible through a combination of physical construction, embedded electronics, colour sensing and audio storytelling.
