
import serial
import json
import time
import statistics

# ==========================================
# SETTINGS
# ==========================================

SERIAL_PORT = "COM11"
BAUD_RATE = 115200

CALIBRATION_FILE = "colour_calibration.json"

SAMPLES = 30
MIN_CHANNEL_SCALE = 20
DISTANCE_THRESHOLD = 2.5

COLOURS = [
    "red",
    "orange",
    "yellow",
    "green",
    "blue"
]


# ==========================================
# LOAD CALIBRATION
# ==========================================

with open(CALIBRATION_FILE, "r") as file:
    calibration = json.load(file)

for colour in COLOURS:
    if colour not in calibration:
        raise ValueError(
            f"Missing calibration for {colour}"
        )

print("Loaded five-colour calibration.")


# ==========================================
# SERIAL READING
# ==========================================

def read_sensor(esp32):

    line = esp32.readline().decode(
        "utf-8", errors="ignore"
    ).strip()

    if not line.startswith("COLOR_DATA"):
        return None

    parts = line.split(",")

    if len(parts) != 5:
        return None

    try:
        return [int(x) for x in parts[1:]]

    except ValueError:
        return None


# ==========================================
# CLASSIFICATION
# ==========================================

def classify_colour(reading):

    best_colour = "unknown"
    best_distance = float("inf")

    distances = {}

    for colour in COLOURS:

        data = calibration[colour]

        centre = data["centre"]
        scale = data["scale"]

        distance_squared = 0

        for i in range(4):

            difference = (
                reading[i] - centre[i]
            ) / max(scale[i], MIN_CHANNEL_SCALE)

            distance_squared += difference ** 2

        distance = (distance_squared / 4) ** 0.5

        distances[colour] = distance

        if distance < best_distance:
            best_distance = distance
            best_colour = colour

    if best_distance > DISTANCE_THRESHOLD:
        best_colour = "unknown"

    return best_colour, best_distance, distances


# ==========================================
# MEDIAN READING
# ==========================================

def collect_readings(esp32):

    readings = []

    while len(readings) < SAMPLES:

        values = read_sensor(esp32)

        if values is None:
            continue

        readings.append(values)

        print(
            f"\rCollecting: {len(readings)}/{SAMPLES}",
            end=""
        )

    print()

    median_reading = [
        round(statistics.median(
            [reading[channel] for reading in readings]
        ))
        for channel in range(4)
    ]

    return median_reading


# ==========================================
# MAIN TEST
# ==========================================

def main():

    print("\nNIRVANA WHEEL - FIVE COLOUR TEST")

    esp32 = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=1
    )

    try:

        time.sleep(2)
        esp32.reset_input_buffer()

        print("\nSensor connected.")
        print("Allowing 60 seconds for warm-up.")

        start = time.monotonic()

        while time.monotonic() - start < 60:

            read_sensor(esp32)

            remaining = 60 - int(
                time.monotonic() - start
            )

            print(
                f"\rWarm-up remaining: {remaining}s ",
                end=""
            )

        print("\n\nWarm-up complete.")

        correct = 0
        total = 0

        while True:

            print("\nAvailable colours:", ", ".join(COLOURS))

            expected = input(
                "\nPlace a colour and enter its name "
                "(or Q to quit): "
            ).strip().lower()

            if expected == "q":
                break

            if expected not in COLOURS:
                print("Invalid colour.")
                continue

            print(
                f"\nKeep {expected.upper()} stationary."
            )

            time.sleep(2)

            esp32.reset_input_buffer()

            reading = collect_readings(esp32)

            predicted, distance, distances = classify_colour(
                reading
            )

            total += 1

            if predicted == expected:
                correct += 1
                result = "CORRECT"
            else:
                result = "INCORRECT"

            print("\n------------------------------")
            print("EXPECTED :", expected.upper())
            print("DETECTED :", predicted.upper())
            print("RESULT   :", result)
            print("READING  :", reading)
            print(f"DISTANCE : {distance:.3f}")

            print("\nDistances to each calibrated colour:")

            for colour, value in sorted(
                distances.items(),
                key=lambda item: item[1]
            ):
                print(f"{colour:8}: {value:.3f}")

            print("------------------------------")

            print(
                f"\nAccuracy: {correct}/{total} "
                f"({correct / total * 100:.1f}%)"
            )

    finally:

        esp32.close()
        print("\nTest finished.")


if __name__ == "__main__":
    main()
