'''
receive BNO055 sensor data from USB and display a graph
'''

import serial
import matplotlib.pyplot as plt
from collections import deque
import numpy as np


def read_BNO055_from_serial(ser):
    package_len = 23 * 4  # 23 floats, each 4 bytes

    # Read bytes until we find the frame marker
    while True:
        data = ser.read(2)
        if data == FRAME_MARKER:
            break

    # Preallocate a numpy array for the frame data
    data = np.empty(package_len * 4, dtype=np.uint8)

    # Read the frame data into the numpy array
    for i in range(package_len):
        data[i] = ser.read(1)[0]

    # Convert the bytes to a numpy array of floats
    values = np.frombuffer(data, dtype=np.float32)

    # Decode the values
    temperature = values[0]
    acceleration = tuple(values[1:4])
    magnetic = tuple(values[4:7])
    gyro = tuple(values[7:10])
    euler = tuple(values[10:13])
    quaternion = tuple(values[13:17])
    linear_acceleration = tuple(values[17:20])
    gravity = tuple(values[20:23])
    
    return temperature, acceleration, magnetic, gyro, euler, quaternion, linear_acceleration, gravity


def display_graph(linear_acceleration, history):
    # Append new values to the history
    history.append(linear_acceleration)

    # Discard the oldest values if the history is too long
    if len(history) > 100:  # Adjust this value to change the X scale
        history.popleft()

    # Display the graph
    for i, color in zip(range(3), ['r', 'g', 'b']):
        plt.plot([x[i] for x in history], color=color)
    plt.draw()
    plt.pause(0.001)
    plt.clf()




if __name__ == "__main__":
    
    port = 'COM3'
    FRAME_MARKER = b'\xAA\xAA'  # Define the 2-byte frame marker
    
    history = deque()  # Use a deque for efficient removal of oldest values

    with serial.Serial(port, 921600, timeout=1) as ser:  # baudrate is irrelevant for USB-CDC
        plt.ion()  # Turn on interactive mode
        while True:
            values = read_BNO055_from_serial(ser)
            
            if values is not None:
                temperature, acceleration, magnetic, gyro, euler, quaternion, linear_acceleration, gravity = values

                # print("Temperature:", temperature)
                # print("Acceleration:", acceleration, "Length:", len(acceleration))
                # print("Magnetic:", magnetic, "Length:", len(magnetic))
                # print("Gyro:", gyro, "Length:", len(gyro))
                # print("Euler:", euler, "Length:", len(euler))
                # print("Quaternion:", quaternion, "Length:", len(quaternion))
                # print("Linear acceleration:", linear_acceleration, "Length:", len(linear_acceleration))
                # print("Gravity:", gravity, "Length:", len(gravity))
                
                display_graph(linear_acceleration, history)
            else:
                print("Resynchronizing...")

    plt.ioff()  # Turn off interactive mode
    plt.show()
