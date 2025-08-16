import numpy as np

# AP positions (x, y) and estimated distances
APs = [(0, 0), (10, 0), (5, 10)]  # Example coordinates
distances = [4, 6.1, 4.8]       # Estimated from RSSI

# Trilateration using least squares
def trilateration(APs, distances):
    A = []
    b = []
    for i in range(1, len(APs)):
        x_i, y_i = APs[i]
        x_1, y_1 = APs[0]
        d_i, d_1 = distances[i], distances[0]
        A.append([2*(x_i - x_1), 2*(y_i - y_1)])
        b.append(d_1**2 - d_i**2 + x_i**2 + y_i**2 - x_1**2 - y_1**2)
    A = np.array(A)
    b = np.array(b)
    return np.linalg.lstsq(A, b, rcond=None)[0]  # Returns (x, y)

position = trilateration(APs, distances)
print(f"Estimated position: {position}")