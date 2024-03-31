'''
send MLX90640 sensor data over USB CDC
'''

import board                        # type: ignore
import busio                        # type: ignore
import adafruit_mlx90640            # type: ignore
from usb_cdc import data as ser     # type: ignore
import asyncio
import struct

FRAME_MARKER = b'\xFF\xFF\xFF\xFF'
FRAME_SHAPE = (24, 32)
NUM_PIXELS = FRAME_SHAPE[0] * FRAME_SHAPE[1]

i2c = busio.I2C(board.GP17, board.GP16, frequency=1000000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
frame = [0] * 768

async def read_sensor_data():
    """Read data from the sensor and return it as bytes."""
    while True:
        try:
            mlx.getFrame(frame)
        except ValueError:
            continue

        # Convert the frame data to bytes and prepend the frame marker
        return FRAME_MARKER + bytes(frame)

async def send_data(data):
    """Send data and return the number of bytes sent."""
    ser.write(data)
    return len(data)

async def main():
    try:
        while True:
            sensor_data = await read_sensor_data()
            if sensor_data is not None:
                await send_data(sensor_data)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())