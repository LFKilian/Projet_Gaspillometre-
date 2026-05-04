from picamera2 import Picamera2
import cv2


picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()
num = 0

print("Appuyez sur 'q' pour quitter.")

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
            if area > un_pour_cent * 35:
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area)/hull_area if hull_area > 0 else 0
                if solidity > 0.9:
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect_ratio = float(w)/h
                    if 1.1 < aspect_ratio < 2.2:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
                        cv2.putText(frame, f"PLATEAU ({int(solidity*100)}%)", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        BOOL = True
            else:
                BOOL = False
                        
        cv2.imshow("Camera", frame)

        if BOOL:
            filename = f"Capture/capture_{num}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Photo prise : {filename}")
            num += 1
            
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
except Exception as e:
    print(f"Erreur : {e}")
    

finally:        
    picam2.stop()
    cv2.destroyAllWindows()
