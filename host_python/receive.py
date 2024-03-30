import serial
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt

def apply_colormap(image, vmin=-40, vmax=300):
    # Apply the colormap using matplotlib
    image_colored = plt.get_cmap('hot')((image - vmin) / (vmax - vmin))

    # Convert the image from RGBA to RGB and scale to the range 0-255
    image_colored = cv2.cvtColor(image_colored.astype(np.float32), cv2.COLOR_RGBA2RGB)
    image_colored = (image_colored * 255).astype(np.uint8)

    return image_colored

def main(port):
    # Open the serial port
    with serial.Serial(port, 9600, timeout=1) as ser:
        frame_marker_len = len(frame_marker)
        buffer = bytearray(frame_marker_len)
        bytes_since_marker = 0  # Add this line

        while True:
            # Read one byte
            byte = ser.read(1)
            if byte:
                # Add the byte to the end of the buffer and remove the first byte
                buffer.append(byte[0])
                del buffer[0]
                bytes_since_marker += 1  # Increment the counter

                # Check if the buffer matches the frame marker
                if buffer == frame_marker:
                    bytes_since_marker = 0  # Reset the counter

                    # Read bytes until we have enough data for a full frame
                    data = bytearray()
                    while len(data) < num_pixels * 4:
                        data.extend(ser.read(num_pixels * 4 - len(data)))
                    if len(data) == num_pixels * 4:
                        # Convert the bytes to a numpy array
                        image = np.frombuffer(data, dtype=np.float32).reshape(frame_shape)

                        # Apply the colormap
                        image_colored = apply_colormap(image)

                        # Resize the image
                        image_colored = cv2.resize(image_colored, (320, 240), interpolation = cv2.INTER_NEAREST)

                        # Display the image using OpenCV
                        cv2.imshow('Image', image_colored)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                    # Read the next frame marker
                    next_frame_marker = ser.read(frame_marker_len)
                    if next_frame_marker != frame_marker:
                        print("Resynchronizing...")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    port = 'COM5'
    frame_marker = b'\xFF\xFF\xFF\xFF'
    frame_shape = (24, 32)
    num_pixels = frame_shape[0] * frame_shape[1]

    main(port)