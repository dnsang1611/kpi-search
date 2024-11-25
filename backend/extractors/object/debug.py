import cv2
import numpy as np

# Example image in RGB format
image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)

# Attempt to convert RGB to BGR with slicing
image_bgr = image[:, :, ::-1]

# This can cause errors in OpenCV functions like cv2.rectangle
cv2.rectangle(image_bgr, (50, 50), (250, 250), (255, 0, 0), 2)  # Might cause error
