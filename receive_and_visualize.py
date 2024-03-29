'''
receive thermal camera data from the Pico over USB-CDC and visualize them
'''

import serial
import collections
import struct
import numpy as np
import cv2
import matplotlib.pyplot as plt

port = 'COM3'
baud = 460800
frame_marker = b'\xFF\xFF\xFF\xFF'
frame_shape = (24, 32)
num_pixels = frame_shape[0] * frame_shape[1]

# Create a colormap.
cmap = plt.get_cmap('hot')

# Open the serial port that the Pico is connected to.
ser = serial.Serial(port, baud)

# Create a deque to hold the last four bytes.
last_four_bytes = collections.deque(maxlen=4)

while True:
    # Read bytes one at a time.
    byte = ser.read(1)
    last_four_bytes.append(byte)

    # Check if the last four bytes are the frame marker.
    if bytes(last_four_bytes) == frame_marker:
        # Read the temperature values.
        data = ser.read(num_pixels * 4)
        values = struct.unpack('<' + 'f' * num_pixels, data)

        # Convert the values to a numpy array and reshape it to the shape of the image.
        img = np.array(values).reshape(frame_shape)

        # Normalize the values to the range 0-1.
        img = cv2.normalize(img, None, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)

        # Apply the colormap and display the image.
        plt.imshow(img, cmap=cmap)
        plt.colorbar(label='Temperature (°C)')
        plt.pause(0.01)  # Update the plot