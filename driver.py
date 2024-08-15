from model import get_model_from_file
import numpy as np
import cv2

model = get_model_from_file()
model.summary()

with open("F:\\Documents\\python_projects\\zain_ai\\frame_parsing\\output\\pikmin.raw", "rb") as f:
    data = f.read()

# Convert byte array to numpy array and reshape
image_np = np.frombuffer(data, dtype=np.uint8)
image_np = image_np.reshape((524, 636, 4))  # 4 channels for RGBA

# Convert RGBA to RGB
image_rgb = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
image_rgb = cv2.resize(image_rgb, (318, 262))

input_frames = np.array([[image_rgb for i in range(10)]])

output = model.predict(input_frames)
print(output)