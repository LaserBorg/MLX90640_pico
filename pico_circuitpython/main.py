'''
send data and log transfer rate.
'''

import board                        # type: ignore
import busio                        # type: ignore
import adafruit_mlx90640            # type: ignore
from usb_cdc import data as ser     # type: ignore
from ulab import numpy as np        # type: ignore
import asyncio

FRAME_MARKER = b'\xAA\xAA'
FRAME_SHAPE = (24, 32)
NUM_PIXELS = FRAME_SHAPE[0] * FRAME_SHAPE[1]

SDA_pin = board.GP16
SCL_pin = board.GP17

i2c = busio.I2C(SCL_pin, SDA_pin, frequency=400000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
frame = [0] * 768

async def read_sensor_data():
    """Read data from the sensor and return it as bytes."""
    try:
        mlx.getFrame(frame)
    except ValueError:
        # retry
        return None

    # return FRAME_MARKER + bytes(frame)
    frame_matrix = np.array(frame, dtype=np.float).reshape(FRAME_SHAPE)  # Convert the frame data to a 24x32 numpy matrix
    return FRAME_MARKER + frame_matrix.tobytes()  # Convert the numpy matrix to bytes and prepend the frame marker

async def send_data(data):
    """Send data and return the number of bytes sent."""
    ser.write(data)
    return len(data)

async def main():
    while True:
        sensor_data = await read_sensor_data()
        if sensor_data is not None:
            await send_data(sensor_data)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
