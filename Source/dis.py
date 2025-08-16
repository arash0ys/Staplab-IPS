import serial
import math

# === Settings ===
SERIAL_PORT = 'COM8'      # Change to your actual port
BAUD_RATE = 115200
TX_POWER = -45            # RSSI at 1 meter (you should calibrate this)
PATH_LOSS_EXPONENT = 2.4  # Environment-dependent (2 = free space, 3 = indoor, 4+ = heavy walls)

def estimate_distance(rssi, tx_power=TX_POWER, n=PATH_LOSS_EXPONENT):
    return 10 ** ((tx_power - rssi) / (10 * n))

def main():
    print(f"Connecting to {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    while True:
        try:
            line = ser.readline().decode().strip()
            if not line:
                continue

            parts = line.split(',')
            if len(parts) != 2:
                continue

            bssid = parts[0]
            rssi = int(parts[1])
            distance = estimate_distance(rssi)

            print(f"BSSID: {bssid} | RSSI: {rssi} dBm | Distance: {distance:.2f} m")

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
