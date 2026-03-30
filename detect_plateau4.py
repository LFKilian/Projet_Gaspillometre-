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
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        blur = cv2.medianBlur(gray, 15)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            un_pour_cent = 1333.33

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            filename = f"Capture/capture_{num}.jpg"
            cv2.imwrite(filename, frame)
            num+=1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
except Exception as e:
    print(f"Erreur : {e}")
    

finally:        
    picam2.stop()
    cv2.destroyAllWindows()
