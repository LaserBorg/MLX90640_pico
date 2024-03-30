# Fast (23 fps) MLX90640 based Thermal Camera for Raspberry Pi Pico (RP2040)

A simple but fast Thermal Imaging Camera using the MLX90640 sensor and USB-CDC

## Features
- fast: 23 frames per second by employing both cores of the RP2040 (whereas a single core would only result in 11 fps):
  - core0 fetches the pages from the MLX90640
  - core1 handles USB-CDC


## Code Based on
- unmodified Melexis Driver: https://github.com/melexis/mlx90640-library/
- the [Pico SDK](https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html)

## Hardware
- Raspberry Pi Pico or Pico W (RP2040)
- MLX90640 Thermal Camera Breakout (55º or 110º), e.g. [Pimoroni](https://shop.pimoroni.com/products/mlx90640-thermal-camera-breakout)


### Wiring

Connect the MLX90640 and the OLED to the 3.3 V Pin 36 of the Raspberry PI Pico.

| MLX90640 | RP2040   | GPIO | Pin |
| -------- | -------- | ---- | --- |
| SDA      | I2C0 SDA | 16   | 21  |
| SDC      | I2C0 SDC | 17   | 22  |


## Building
- make sure the "[Pico SDK](https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html)" is installed and the environment variable "PICO_SDK_PATH" refers to it.
- `git clone https://github.com/LaserBorg/MLX90640_pico.git -b main --depth 1`
- `cd MLX90640_pico`
- `git submodule init`
- `git submodule update --recursive`
- `mkdir build`
- `cd build`
- `export PICO_SDK_PATH=/home/flip/pico/pico-sdk`
- `cmake .. -DPICO_BOARD=pico_w`
- `make -j8`

## More Images

![breadboard setup showing thermal image of a candle](images/photo_1.jpg)

![close-up of OLED display showing camera](images/photo_2.jpg)

## other

- heat map inspiration: http://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients