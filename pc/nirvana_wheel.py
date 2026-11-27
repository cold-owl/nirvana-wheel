
import serial
import time
import pygame
import json
import math
import statistics

from pathlib import Path
from collections import deque

from display import show_result
from nirvana_paths import get_path


# =====================================================
# CONFIGURATION
# =====================================================

SERIAL_PORT = "COM11"
BAUD_RATE = 115200

BASE_DIR = Path(__file__).resolve().parent

AUDIO_FOLDER = BASE_DIR / "audio"
CALIBRATION_FILE = BASE_DIR / "colour_calibration.json"

CALIBRATION_MODE = False

STABLE_READINGS = 5
DISTANCE_THRESHOLD = 0.15

# These names MUST match calibration JSON keys.
# They are sensor labels, not necessarily Dharma path names.
COLOURS = [
    "red", "orange", "yellow", "green",
    "blue", "indigo", "violet", "white"
]

# Map sensor labels to Dharma path labels.
# Change these according to your actual physical colour mapping.
SENSOR_TO_PATH = {
    "red": "red",
    "orange": "orange",
    "yellow": "yellow",
    "green": "green",
    "blue": "blue",
    "indigo": "purple",
    "violet": "violet",
    "white": "brown",
}


# =====================================================
# GLOBAL STATE
# =====================================================

calibration_data = {}
last_colour = None


# =====================================================
# SERIAL READING
# =====================================================

def read_sensor(esp):

    line = esp.readline().decode(
        "utf-8", errors="ignore"
    ).strip()

    if not line:
        return None

    # Format A:
    # COLOR_DATA,1250,820,640,2100

    if line.startswith("COLOR_DATA,"):

        try:
            values = [
                float(x) for x in line.split(",")[1:]
            ]

            if len(values) == 4 and all(
                math.isfinite(x) and x > 0 for x in values
            ):
                return values

        except ValueError:
            return None

    # Format B:
    # R=1250 G=820 B=640 C=2100

    try:

        parts = line.replace("=", " ").split()

        if len(parts) == 8:

            if (
                parts[0] == "R"
                and parts[2] == "G"
                and parts[4] == "B"
                and parts[6] == "C"
            ):

                values = [
                    float(parts[1]),
                    float(parts[3]),
                    float(parts[5]),
                    float(parts[7])
                ]

                if all(
                    math.isfinite(x) and x > 0
                    for x in values
                ):
                    return values

    except (ValueError, IndexError):
        pass

    return None


# =====================================================
# FEATURE EXTRACTION
# =====================================================

def make_features(readings):

    features = []

    for r, g, b, clear in readings:

        total = r + g + b

        if total <= 0:
            continue

        features.append([
            r / total,
            g / total,
            b / total,
            clear / total
        ])

    if not features:
        return None

    return [
        statistics.median(
            [row[i] for row in features]
        )
        for i in range(4)
    ]


# =====================================================
# LOAD CALIBRATION
# =====================================================

def load_calibration():

    global calibration_data

    if not CALIBRATION_FILE.exists():
        return False

    try:

        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)

        for colour in COLOURS:

            if colour not in data:
                print("Missing calibration:", colour)
                return False

            if len(data[colour]) != 4:
                print("Invalid calibration:", colour)
                return False

        calibration_data = data

        print("Calibration loaded successfully.")

        return True

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        KeyError
    ):

        print("Could not load calibration.")
        return False


# =====================================================
# CLASSIFICATION
# =====================================================

def classify_colour(reading):

    feature = make_features([reading])

    if feature is None:
        return "unknown", float("inf")

    best_colour = "unknown"
    best_distance = float("inf")

    for colour, centre in calibration_data.items():

        distance = math.sqrt(
            sum(
                (feature[i] - centre[i]) ** 2
                for i in range(4)
            )
        )

        if distance < best_distance:

            best_distance = distance
            best_colour = colour

    if best_distance > DISTANCE_THRESHOLD:
        return "unknown", best_distance

    return best_colour, best_distance


# =====================================================
# AUDIO PLAYBACK
# =====================================================

def play_path(colour):

    path = get_path(colour)

    if not path:
        print("No path found:", colour)
        return

    print("\n" + "=" * 50)
    print("SELECTED:", path["name"])
    print("=" * 50)

    print(path["description"])

    audio_path = AUDIO_FOLDER / path["audio"]

    if not audio_path.exists():

        print("Audio file missing:", audio_path)
        return

    pygame.mixer.music.stop()
    pygame.mixer.music.load(str(audio_path))
    pygame.mixer.music.play()

    print("Playing:", path["audio"])


# =====================================================
# MAIN PROGRAM
# =====================================================

def main():

    global last_colour

    print("\n================================")
    print("          NIRVANA WHEEL")
    print("================================")

    esp = None
    mixer_ready = False

    try:

        pygame.mixer.init()
        mixer_ready = True

        print(f"Connecting to {SERIAL_PORT}...")

        esp = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        )

        time.sleep(2)
        esp.reset_input_buffer()

        print("ESP32 connected!")

        if CALIBRATION_MODE:

            print("Calibration mode enabled.")
            print("Run tcs3200_test.py first.")
            return

        if not load_calibration():

            print("No valid calibration found.")
            print("Run tcs3200_test.py first.")
            return

        # Check sensor readings before entering loop
        print("\nChecking sensor readings...")

        start = time.monotonic()
        first_reading = None

        while time.monotonic() - start < 10:

            first_reading = read_sensor(esp)

            if first_reading is not None:
                break

        if first_reading is None:

            print("No valid sensor readings received.")
            return

        print("Sensor data received:", first_reading)

        print("\nWaiting for stable colour...\n")

        recent_colours = deque(
            maxlen=STABLE_READINGS
        )

        while True:

            reading = read_sensor(esp)

            if reading is None:
                continue

            colour, distance = classify_colour(reading)

            print(
                f"Reading: {reading} | "
                f"Detected: {colour} | "
                f"Distance: {distance:.5f}"
            )

            recent_colours.append(colour)

            if len(recent_colours) < STABLE_READINGS:
                continue

            if len(set(recent_colours)) != 1:
                continue

            stable_colour = recent_colours[0]

            if stable_colour == "unknown":

                last_colour = None
                continue

            if stable_colour != last_colour:

                last_colour = stable_colour

                print(
                    "\nSTABLE COLOUR DETECTED:",
                    stable_colour.upper()
                )

                # Convert sensor label into Dharma path label.
                path_colour = SENSOR_TO_PATH.get(stable_colour)

                if path_colour is None:
                    print("No Dharma mapping for:", stable_colour)
                    continue

                # Verify that a path exists before showing it.
                path = get_path(path_colour)

                if not path:
                    print("No Dharma path found:", path_colour)
                    continue

                # Lottery animation and reveal.
                show_result(path_colour)

                # Play the corresponding audio.
                play_path(path_colour)

    except serial.SerialException as error:

        print("\nSERIAL CONNECTION ERROR:", error)
        print("Close PlatformIO Serial Monitor and check COM11.")

    except KeyboardInterrupt:

        print("\nStopping Nirvana Wheel...")

    finally:

        if esp is not None and esp.is_open:
            esp.close()

        if mixer_ready:
            pygame.mixer.music.stop()
            pygame.mixer.quit()

        pygame.quit()


if __name__ == "__main__":
    main()
