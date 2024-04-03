'''
based on
https://github.com/mwerezak/micropython-mlx90640/tree/master

using micropython 1.23 build with ulab:
https://github.com/v923z/micropython-builder
https://micropython-ulab.readthedocs.io/en/latest/
'''

import math

from ulab import numpy as np            # type: ignore
from machine import Pin, I2C, UART      # type: ignore
import uasyncio                         # type: ignore
import micropython                      # type: ignore

import mlx90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern


PIN_I2C_SDA = Pin(16, Pin.IN, Pin.PULL_UP)
PIN_I2C_SCL = Pin(17, Pin.IN, Pin.PULL_UP)

I2C_CAMERA = I2C(id=0, scl=PIN_I2C_SCL, sda=PIN_I2C_SDA)

FRAME_MARKER = b'\xAA\xAA'


class Config:
    def __init__(self):
        self.refresh_rate = 16
        self.min_scale = 8
        self.debug = False
        # self.bad_pixels = (30, 31, 63, 127, 191, 481, 482, 483, 484, 485, 486, 487, 
        #                    488, 489, 490, 491, 492, 493, 494, 495, 703, 735, 767)
        

class CameraLoop:
    def __init__(self):
        config = Config()

        self.camera = mlx90640.detect_camera(I2C_CAMERA)
        self.camera.set_pattern(ChessPattern)  # InterleavedPattern
        self.camera.refresh_rate = config.refresh_rate
        self._refresh_period = math.ceil(1000/self.camera.refresh_rate)

        # self.bad_pix = config.bad_pixels
        self.debug = config.debug

        self.update_event = uasyncio.Event()
        self.state = None
        self.image = None


    async def run(self):
        await uasyncio.sleep_ms(80 + 2 * int(self._refresh_period))
        print("setup camera...")
        self.camera.setup()
        self.image = self.camera.image

        tasks = [self.stream_images(),]
        if self.debug:
            tasks.append(self.print_mem_usage())
        await uasyncio.gather(*tasks)

    def _calc_temp(self, idx):
        return self.image.calc_temperature(idx, self.state)

    def _calc_temp_ext(self, idx):
        return self.image.calc_temperature_ext(idx, self.state)

    def calc_reticle_temperature(self):
        reticle = (367, 368, 399, 400)
        temp = sum(self._calc_temp_ext(idx) for idx in reticle)
        return temp/4

    async def wait_for_data(self):
        await uasyncio.wait_for_ms(self._wait_inner(), int(self._refresh_period))

    async def _wait_inner(self):
        while not self.camera.has_data:
            await uasyncio.sleep_ms(50)

    async def stream_images(self):
        print("start image read loop...")
        sp = 0

        # # Initialize UART
        # uart = UART(0, baudrate=921600)

        while True:
            await self.wait_for_data()
            
            self.camera.read_image(sp)

            self.state = self.camera.read_state()
            self.image = self.camera.process_image(sp, self.state)
            # self.image.interpolate_bad_pixels(self.bad_pix)

            frame = np.array(self.image.buf).reshape((NUM_ROWS, NUM_COLS))
            np.ndinfo(frame)

            # # BUG: not yet working for USB
            # uart.write(FRAME_MARKER + self.image.buf)  # str(frame.tolist())

            sp = int(not sp)
            self.update_event.set()

            await uasyncio.sleep_ms(int(self._refresh_period * 0.8))

    async def print_mem_usage(self):
        while True:
            await uasyncio.sleep(5)
            micropython.mem_info()


if __name__ == "__main__":
    main = CameraLoop()
    uasyncio.run(main.run())
