'''
send data and log transfer rate.
'''

import time
import board                        # type: ignore
import busio                        # type: ignore
import adafruit_mlx90640            # type: ignore
from usb_cdc import data as ser     # type: ignore
from ulab import numpy as np        # type: ignore

FRAME_MARKER = b'\xFF\xFF\xFF\xFF'
FRAME_SHAPE = (24, 32)
NUM_PIXELS = FRAME_SHAPE[0] * FRAME_SHAPE[1]

i2c = busio.I2C(board.GP17, board.GP16, frequency=800000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
frame = [0] * 768

def read_sensor_data():
    """Read data from the sensor and return it as bytes."""
    try:
        mlx.getFrame(frame)
    except ValueError:
        # these happen, no biggie - retry
        return None

    # Convert the frame data to a 24x32 numpy matrix
    frame_matrix = np.array(frame, dtype=np.float).reshape(FRAME_SHAPE)

    # Convert the numpy matrix to bytes and prepend the frame marker
    return FRAME_MARKER + frame_matrix.tobytes()

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
            sensor_data = read_sensor_data()
            if sensor_data is not None:
                bytes_sent += send_data(sensor_data)
                if calculate_transfer_rate(bytes_sent, start_time):
                    start_time = time.time()
                    bytes_sent = 0
    except Exception as e:
        print(f"An error occurred: {e}")