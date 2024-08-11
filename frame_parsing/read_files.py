from PIL import Image
import io
import numpy as np
import cv2 


# frames are rendered by dolphin in fullscreen at 1312 by 1080 636 x 524
# if using avi as data to learn from, 
height = 1312
width = 1080

with open("F:\\Documents\\python_projects\\zain_ai\\frame_parsing\\output\\pikmin.raw", "rb") as f:
    data = f.read()

# Convert byte array to numpy array and reshape
image_np = np.frombuffer(data, dtype=np.uint8)
image_np = image_np.reshape((524, 636, 4))  # 4 channels for RGBA

# Convert RGBA to RGB
image_rgb = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)

vcap = cv2.VideoCapture("F:\\Documents\\python_projects\\zain_ai\\frame_parsing\\avi_output\\pikmin.avi")
if vcap.isOpened(): 
    # get vcap property 
    width  = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`

    # checks whether frames were extract
    success, image = vcap.read()
    last_frame_num = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
    image_rgb2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

cv2.imshow("Input", image_rgb)
cv2.waitKey(0)
print("hi") 