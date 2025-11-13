import cv2
import numpy as np

def nothing(x):
    pass

# Capture webcam
cap = cv2.VideoCapture(0)
cv2.namedWindow("Tuner")

# Create Sliders for Hue, Saturation, Value (Low and High)
# Default values set for a typical Orange/Red Arduino LED
cv2.createTrackbar("L - H", "Tuner", 0, 179, nothing)
cv2.createTrackbar("L - S", "Tuner", 100, 255, nothing)
cv2.createTrackbar("L - V", "Tuner", 100, 255, nothing)
cv2.createTrackbar("U - H", "Tuner", 179, 179, nothing)
cv2.createTrackbar("U - S", "Tuner", 255, 255, nothing)
cv2.createTrackbar("U - V", "Tuner", 255, 255, nothing)

print("INSTRUCTIONS:")
print("1. Turn your Arduino LED ON (make it solid ON if possible for setup).")
print("2. Move sliders until the LED is WHITE and background is BLACK.")
print("3. Write down the 'Lower' and 'Upper' arrays printed in the terminal.")

while True:
    _, frame = cap.read()
    
    # Convert BGR to HSV (Hue Saturation Value)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get slider positions
    l_h = cv2.getTrackbarPos("L - H", "Tuner")
    l_s = cv2.getTrackbarPos("L - S", "Tuner")
    l_v = cv2.getTrackbarPos("L - V", "Tuner")
    u_h = cv2.getTrackbarPos("U - H", "Tuner")
    u_s = cv2.getTrackbarPos("U - S", "Tuner")
    u_v = cv2.getTrackbarPos("U - V", "Tuner")

    # Create the Mask
    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])
    
    mask = cv2.inRange(hsv, lower_range, upper_range)
    
    # show the mask
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Stack images to see side-by-side
    # Resize for fitting on screen
    scale = 0.5
    frame_s = cv2.resize(frame, None, fx=scale, fy=scale)
    result_s = cv2.resize(result, None, fx=scale, fy=scale)
    mask_s = cv2.resize(cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), None, fx=scale, fy=scale)
    
    cv2.imshow("Tuner", np.hstack([frame_s, mask_s, result_s]))
    
    key = cv2.waitKey(1)
    if key == 27: # Esc key
        break
    if key == ord('s'):
        print(f"SAVED SETTINGS: Lower={lower_range}, Upper={upper_range}")

cap.release()
cv2.destroyAllWindows()