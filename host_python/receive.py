'''
receive MLX90640 sensor data from USB and display it
'''

import serial
import struct
import numpy as np
import cv2
import matplotlib.cm as cm
from matplotlib import colors


def read_thermal_from_serial(ser):
    frame_marker_len = len(frame_marker)
    buffer = bytearray(frame_marker_len)
    bytes_since_marker = 0

    while True:
        # Read one byte
        byte = ser.read(1)
        if byte:
            # Add the byte to the end of the buffer and remove the first byte
            buffer.append(byte[0])
            del buffer[0]
            bytes_since_marker += 1

            # Check if the buffer matches the frame marker
            if buffer == frame_marker:
                bytes_since_marker = 0

                # Read bytes until we have enough data for a full frame
                data = bytearray()
                while len(data) < num_pixels * 4:
                    data.extend(ser.read(num_pixels * 4 - len(data)))
                if len(data) == num_pixels * 4:
                    # Convert the bytes to a numpy array
                    image = np.array(struct.unpack('f' * num_pixels, data)).astype(np.float32).reshape(frame_shape)

                    # Flip the image vertically
                    image = np.flip(image, 0)

                    # print(f"Min: {np.min(image)}, Max: {np.max(image)}")  # Print the min and max values
                    return image

def display_thermal(thermal_map, size=(320, 240)):

    def apply_cmap(thermal_map, vmin=None, vmax=None):
        # If vmin and vmax are not specified, set them to the 5th and 95th percentiles of the data
        if vmin is None:
            vmin = np.percentile(thermal_map, 5)
        if vmax is None:
            vmax = np.percentile(thermal_map, 95)

        # Normalize the thermal map to the vmin-vmax range
        normalized_map = (thermal_map - vmin) / (vmax - vmin)

        # apply the colormap
        cmap = cm.ScalarMappable(cmap='CMRmap', norm=colors.Normalize(vmin=0, vmax=1))
        cmapped_image = cmap.to_rgba(normalized_map)

        cmapped_image = cv2.cvtColor((cmapped_image * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        return cmapped_image

    cmapped_image = apply_cmap(thermal_map.copy())
    cmapped_image = cv2.resize(cmapped_image, size, interpolation = cv2.INTER_NEAREST)
    cv2.imshow('Image', cmapped_image)


if __name__ == "__main__":
    port = 'COM5'
    frame_marker = b'\xFF\xFF\xFF\xFF'
    frame_shape = (24, 32)  # MLX90640: 32 rows, 24 columns
    num_pixels = frame_shape[0] * frame_shape[1]

    with serial.Serial(port, 115200, timeout=1) as ser:  # baudrate is irrelevant for USB-CDC
        while True:
            thermal_map = read_thermal_from_serial(ser)
            if thermal_map is not None:
                display_thermal(thermal_map)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Resynchronizing...")

    cv2.destroyAllWindows()
