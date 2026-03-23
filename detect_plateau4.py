from picamera2 import Picamera2
import cv2


picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()
num = 0

try:
    while True:
        frame = picam2.capture_array()
        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            filename = f"Capture/capture_{num}.jpg"
            cv2.imwrite(filename, frame)
        

except Exception as e:
    print(f"Erreur : {e}")
    

finally:        
    picam2.stop()
    cv2.destroyAllWindows()
