
import serial
import time
import json
import statistics
import math
from pathlib import Path

# =====================================================
# CONFIGURATION
# =====================================================

PORT = "COM11"
BAUD = 115200

BASE_DIR = Path(__file__).resolve().parent
CALIBRATION_FILE = BASE_DIR / "colour_calibration.json"

COLOURS = [
    "red", "orange", "yellow", "green",
    "blue", "indigo", "violet", "white"
]

SAMPLES = 100
SETTLING_SECONDS = 3


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
# COLLECT SENSOR READINGS
# =====================================================

def collect_samples(esp, count=SAMPLES):
    readings = []

    print(f"Collecting {count} readings...")

    while len(readings) < count:

        values = read_sensor(esp)

        if values is None:
            continue

        readings.append(values)

        print(
            f"\rCollecting {len(readings)}/{count}",
            end=""
        )

    print()
    return readings


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
        raise ValueError("No valid colour readings.")

    return [
        statistics.median(
            [row[i] for row in features]
        )
        for i in range(4)
    ]


# =====================================================
# CALIBRATION
# =====================================================

def calibrate(esp):

    calibration = {}

    print("\n========== CALIBRATION ==========")
    print("Keep sensor distance and lighting fixed.")

    for colour in COLOURS:

        input(
            f"\nPlace {colour.upper()} under the sensor "
            "and press ENTER..."
        )

        print(
            f"Settling for {SETTLING_SECONDS} seconds..."
        )

        esp.reset_input_buffer()
        time.sleep(SETTLING_SECONDS)
        esp.reset_input_buffer()

        readings = collect_samples(esp)

        centre = make_features(readings)

        calibration[colour] = centre

        print(
            f"{colour.upper()} features: "
            f"{[round(x, 5) for x in centre]}"
        )

    with open(CALIBRATION_FILE, "w") as file:
        json.dump(calibration, file, indent=4)

    print("\nCalibration saved:", CALIBRATION_FILE)

    return calibration


# =====================================================
# LOAD CALIBRATION
# =====================================================

def load_calibration():

    if not CALIBRATION_FILE.exists():
        raise FileNotFoundError(
            "Calibration file not found. Calibrate first."
        )

    with open(CALIBRATION_FILE, "r") as file:
        calibration = json.load(file)

    for colour in COLOURS:

        if colour not in calibration:
            raise ValueError(
                f"Missing calibration for {colour}"
            )

        if len(calibration[colour]) != 4:
            raise ValueError(
                f"Invalid calibration for {colour}"
            )

    return calibration


# =====================================================
# CLASSIFICATION
# =====================================================

def classify(readings, calibration):

    feature = make_features(readings)

    distances = {}

    for colour, centre in calibration.items():

        distance = math.sqrt(
            sum(
                (feature[i] - centre[i]) ** 2
                for i in range(4)
            )
        )

        distances[colour] = distance

    ordered = sorted(
        distances.items(),
        key=lambda item: item[1]
    )

    return ordered[0][0], ordered


# =====================================================
# TEST COLOURS
# =====================================================

def test_colours(esp, calibration):

    correct = 0
    total = 0

    print("\n========== COLOUR TEST ==========")

    while True:

        expected = input(
            "\nPlace a colour and enter its name "
            "(Q to quit): "
        ).strip().lower()

        if expected == "q":
            break

        if expected not in COLOURS:
            print("Invalid colour.")
            continue

        print("Keep the colour stationary.")

        esp.reset_input_buffer()
        time.sleep(SETTLING_SECONDS)
        esp.reset_input_buffer()

        readings = collect_samples(esp)

        detected, distances = classify(
            readings, calibration
        )

        total += 1

        if detected == expected:
            correct += 1
            result = "CORRECT"
        else:
            result = "INCORRECT"

        print("\nExpected :", expected.upper())
        print("Detected :", detected.upper())
        print("Result   :", result)

        print("\nNearest colours:")

        for colour, distance in distances:
            print(f"{colour:8} {distance:.6f}")

        print(
            f"\nAccuracy: {correct}/{total} "
            f"({correct / total * 100:.1f}%)"
        )


# =====================================================
# MAIN
# =====================================================

def main():

    print("\nNIRVANA WHEEL - TCS3200")

    esp = None

    try:

        esp = serial.Serial(
            PORT,
            BAUD,
            timeout=2
        )

        time.sleep(2)
        esp.reset_input_buffer()

        print("Sensor connected.")

        # Check that readings are arriving
        print("\nChecking sensor readings...")

        first_reading = None
        start = time.monotonic()

        while time.monotonic() - start < 10:
            first_reading = read_sensor(esp)

            if first_reading is not None:
                break

        if first_reading is None:
            print("\nERROR: No valid sensor readings received.")
            print("Check the ESP32 serial output format.")
            return

        print("Sensor data received:", first_reading)

        choice = input(
            "\nType C to calibrate all 8 colours "
            "or T to test existing calibration: "
        ).strip().lower()

        if choice == "c":

            calibration = calibrate(esp)
            test_colours(esp, calibration)

        elif choice == "t":

            calibration = load_calibration()
            test_colours(esp, calibration)

        else:
            print("Invalid choice.")

    except serial.SerialException as error:
        print("\nSERIAL ERROR:", error)

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("\nERROR:", error)

    except KeyboardInterrupt:
        print("\nCalibration stopped.")

    finally:

        if esp is not None and esp.is_open:
            esp.close()

        print("\nFinished.")


if __name__ == "__main__":
    main()
