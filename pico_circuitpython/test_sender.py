'''
send data and log transfer rate.
'''

import time
import random
from usb_cdc import data as ser     # type: ignore
from ulab import numpy as np        # type: ignore

FRAME_MARKER = b'\xFF\xFF\xFF\xFF'
FRAME_SHAPE = (24, 32)
NUM_PIXELS = FRAME_SHAPE[0] * FRAME_SHAPE[1]

def generate_dummy_data():
    """Generate dummy image buffer of the given size."""
    # Create a list of random uint16 numbers
    dummy_data_list = [random.randint(0, 65535) for _ in range(NUM_PIXELS)]
    # Convert the list to a ulab array
    dummy_data = np.array(dummy_data_list, dtype=np.uint16).reshape(FRAME_SHAPE)
    # Convert the array to bytes and prepend the frame marker
    return FRAME_MARKER + dummy_data.tobytes()

def send_data(data):
    """Send data and return the number of bytes sent."""
    ser.write(data)
    return len(data)

def calculate_transfer_rate(bytes_sent, start_time):
    """Calculate and print the transfer rate."""
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:  # Calculate transfer rate every second
        transfer_rate = bytes_sent / elapsed_time
        print(f'Timestamp: {time.time()}, Transfer rate: {transfer_rate / 1024} KB/s')
        return True
    return False

if __name__ == "__main__":
    start_time = time.time()
    bytes_sent = 0

    try:
        while True:
            dummy_data = generate_dummy_data()
            bytes_sent += send_data(dummy_data)
            if calculate_transfer_rate(bytes_sent, start_time):
                start_time = time.time()
                bytes_sent = 0
    except Exception as e:
        print(f"An error occurred: {e}")