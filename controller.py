"""
import serial
import json
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)  # serial module


def classify(light, temp):  # module to classify light and temperature
    score = 100  # productivity score

    # Light scoring
    if light < 300:  # poor lighting
        score -= 20
    elif light < 500:  # ok lighting
        score -= 10

    # Temp scoring
    if temp > 32 or temp < 15:  # temp unsafe
        score -= 35
    elif temp > 27 or temp < 18:  # temp poor
        score -= 20
    elif temp > 24 or temp < 20:  # temp ok
        score -= 10

    return score


def get_state(score):
    if score >= 85:
        return "GREEN"
    elif score >= 65:
        return "YELLOW"
    else:
        return "URGENT"


while True:
    line = ser.readline().decode().strip()

    try:
        data = json.loads(line)
        light = data["light"]
        temp = data["temp"]

        score = classify(light, temp)
        state = get_state(score)

        print(f"Light: {light} | Temp: {temp:.2f}")
        print(f"Score: {score} | State: {state}")
        print("------------------------")

        # Send LED command
        if state == "GREEN":
            ser.write(b"GREEN\n")
        elif state == "YELLOW":
            ser.write(b"YELLOW\n")
        else:
            ser.write(b"URGENT\n")  # flashing later

    except:
        pass

    time.sleep(0.5)
"""
import serial
import json
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)

# --- Pomodoro Timer State ---
session_start = time.time()    # timestamp when session began

FOCUS_THRESHOLDS = {
    "warn":   20 * 60,   # 20 min  → -10, break needed
    "urgent": 40 * 60,   # 40 min  → -20, break urgent
}


def classify(light, temp):
    score = 100

    # Light scoring
    if light < 300:
        score -= 20
        light_msg = "⚠ Poor lighting"
    elif light < 500:
        score -= 10
        light_msg = "~ OK lighting"
    else:
        light_msg = "✓ Ideal lighting"

    # Temp scoring
    if temp > 32 or temp < 15:
        score -= 35
        temp_msg = "✗ Unsafe temperature"
    elif temp > 27 or temp < 18:
        score -= 20
        temp_msg = "⚠ Poor temperature"
    elif temp > 24 or temp < 20:
        score -= 10
        temp_msg = "~ OK temperature"
    else:
        temp_msg = "✓ Ideal temperature"

    return score, light_msg, temp_msg


def classify_focus(elapsed):
    """
    Returns (penalty, message) based on elapsed session time and focus mode.
    Returns (0, None) if still within the ideal focus window.
    """
    thresholds = FOCUS_THRESHOLDS

    if elapsed >= thresholds["urgent"]:
        mins = int(elapsed // 60)
        return -20, f"🚨 Break URGENT — you've been focused for {mins} min. Stop now!"
    elif elapsed >= thresholds["warn"]:
        mins = int(elapsed // 60)
        return -10, f"⏸ Break needed — you've been focused for {mins} min. Rest soon."
    else:
        return 0, None


def get_state(score):
    if score >= 85:
        return "GREEN"
    elif score >= 65:
        return "YELLOW"
    else:
        return "URGENT"


def format_elapsed(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m:02d}m {s:02d}s"


def send_led(state, break_urgent=False):
    """
    LED logic:
    - GREEN state + break urgent → flash green (serial BREAK_FLASH)
    - Otherwise send state as usual
    """
    if break_urgent:
        ser.write(b"BREAK_FLASH\n")
    elif state == "GREEN":
        ser.write(b"GREEN\n")
    elif state == "YELLOW":
        ser.write(b"YELLOW\n")
    else:
        ser.write(b"URGENT\n")


# --- Main loop ---
while True:
    line = ser.readline().decode().strip()

    try:
        data = json.loads(line)
        light = data["light"]
        temp = data["temp"]

        # --- Environment scoring ---
        score, light_msg, temp_msg = classify(light, temp)

        # --- Focus/timer scoring ---
        elapsed = time.time() - session_start
        focus_penalty, focus_msg = classify_focus(elapsed)
        score += focus_penalty  # penalty is negative, so this subtracts
        score = max(0, score)   # floor at 0

        # --- Determine state ---
        state = get_state(score)
        break_urgent = focus_penalty == -20

        # --- Send LED command ---
        send_led(state, break_urgent)

    except Exception:
        pass

    time.sleep(0.5)
