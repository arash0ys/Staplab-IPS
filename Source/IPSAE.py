import pygame
import numpy as np
import sys
import random

# --- PARAMETERS ---
ROOM_SIZE = 10  # meters
GRID_SIZE = 1  # 1m resolution
GRID_COUNT = ROOM_SIZE // GRID_SIZE
CELL_PIXELS = 40  # each cell = 40 pixels on screen
WINDOW_WIDTH = 2 * GRID_COUNT * CELL_PIXELS  # 2 panels side by side
WINDOW_HEIGHT = GRID_COUNT * CELL_PIXELS

# --- RSSI SIMULATION ---
RSSI_0 = -40  # dBm at 1m
PATH_LOSS_EXP = 3
NOISE_STD = 2

# --- ACCESS POINTS ---
ap_positions = [
    (0, 0),
    (ROOM_SIZE, 0),
    (0, ROOM_SIZE),
    (ROOM_SIZE, ROOM_SIZE)
]

# --- INITIALIZE PYGAME ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Indoor Positioning System Simulation")
clock = pygame.time.Clock()
FPS = 60

# --- COLORS ---
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (50, 100, 255)  # real position
RED = (255, 80, 80)    # estimated position
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)    # border line

# --- Real Position State ---
person_pos = [ROOM_SIZE / 2, ROOM_SIZE / 2]  # in meters

# --- Generate Fingerprint Dataset ---
def generate_fingerprint_map():
    fingerprint = np.zeros((GRID_COUNT, GRID_COUNT, len(ap_positions)))
    for y in range(GRID_COUNT):
        for x in range(GRID_COUNT):
            px = x + 0.5
            py = y + 0.5
            for ap_index, (ap_x, ap_y) in enumerate(ap_positions):
                d = np.sqrt((px - ap_x) ** 2 + (py - ap_y) ** 2)
                d = max(d, 1.0)
                rssi = RSSI_0 - 10 * PATH_LOSS_EXP * np.log10(d)
                fingerprint[y, x, ap_index] = rssi
    return fingerprint

fingerprint_map = generate_fingerprint_map()

# --- Simulate RSSI at real position ---
def simulate_rssi(px, py):
    rssi_vector = []
    for ap_x, ap_y in ap_positions:
        d = np.sqrt((px - ap_x) ** 2 + (py - ap_y) ** 2)
        d = max(d, 1.0)
        rssi = RSSI_0 - 10 * PATH_LOSS_EXP * np.log10(d)
        rssi += np.random.normal(0, NOISE_STD)
        rssi_vector.append(rssi)
    return np.array(rssi_vector)

# --- Estimate Position from RSSI ---
def estimate_position(rssi_vector, fingerprint_map):
    min_dist = float('inf')
    best_match = (0, 0)
    for y in range(GRID_COUNT):
        for x in range(GRID_COUNT):
            ref = fingerprint_map[y, x]
            dist = np.linalg.norm(rssi_vector - ref)
            if dist < min_dist:
                min_dist = dist
                best_match = (x, y)
    return best_match

# --- Convert meters to pixels ---
def meter_to_pixel(x_meter, y_meter, offset_x=0):
    return int(offset_x + x_meter * CELL_PIXELS), int(y_meter * CELL_PIXELS)

from collections import deque, Counter

est_history = deque(maxlen=10)  # store last 10 estimates

from collections import deque, Counter
import time

est_history = deque()
last_update_time = time.time()
estimated_cell_to_display = (0, 0)


# --- Main Loop ---
while True:
    dt = clock.tick(FPS) / 1000  # seconds

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Movement ---
    keys = pygame.key.get_pressed()
    speed = 1  # meters per second
    dx = dy = 0
    if keys[pygame.K_LEFT]:
        dx = -speed * dt
    if keys[pygame.K_RIGHT]:
        dx = speed * dt
    if keys[pygame.K_UP]:
        dy = -speed * dt
    if keys[pygame.K_DOWN]:
        dy = speed * dt

    person_pos[0] = max(0, min(ROOM_SIZE, person_pos[0] + dx))
    person_pos[1] = max(0, min(ROOM_SIZE, person_pos[1] + dy))

    # --- Simulate RSSI and store estimated positions ---
    current_rssi = simulate_rssi(*person_pos)
    est = estimate_position(current_rssi, fingerprint_map)
    est_history.append(est)

# --- Update displayed estimated position every 2 seconds ---
    now = time.time()
    if now - last_update_time >= .1:
        if est_history:
            most_common = Counter(est_history).most_common(1)
            estimated_cell_to_display = most_common[0][0]
        est_history.clear()
        last_update_time = now


    # --- Draw ---
    screen.fill(WHITE)

    # Draw grid
    for i in range(GRID_COUNT + 1):
        # Left panel
        pygame.draw.line(screen, GRAY, (0, i * CELL_PIXELS), (GRID_COUNT * CELL_PIXELS, i * CELL_PIXELS))
        pygame.draw.line(screen, GRAY, (i * CELL_PIXELS, 0), (i * CELL_PIXELS, GRID_COUNT * CELL_PIXELS))
        # Right panel
        offset = GRID_COUNT * CELL_PIXELS
        pygame.draw.line(screen, GRAY, (offset, i * CELL_PIXELS), (offset + GRID_COUNT * CELL_PIXELS, i * CELL_PIXELS))
        pygame.draw.line(screen, GRAY, (offset + i * CELL_PIXELS, 0), (offset + i * CELL_PIXELS, GRID_COUNT * CELL_PIXELS))

    # Draw middle border line
    pygame.draw.line(screen, GREEN, (GRID_COUNT * CELL_PIXELS, 0), (GRID_COUNT * CELL_PIXELS, WINDOW_HEIGHT), 3)

    # Real position (left panel)
    px, py = meter_to_pixel(*person_pos)
    pygame.draw.circle(screen, BLUE, (px, py), 8)

    # Estimated position (right panel)
    ex, ey = estimated_cell_to_display
    est_px = GRID_COUNT * CELL_PIXELS + ex * CELL_PIXELS + CELL_PIXELS // 2
    est_py = ey * CELL_PIXELS + CELL_PIXELS // 2
    pygame.draw.rect(screen, RED, (est_px - 8, est_py - 8, 16, 16))


    pygame.display.flip()