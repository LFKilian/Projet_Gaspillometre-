from picamera2 import Picamera2
import cv2
import subprocess
from send_api import envoyer_analyse_api
from send_api import ajouter_log
import threading
import argparse

picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()
num = 0
BOOL=False
plateau_deja_vu = True

parser = argparse.ArgumentParser(description="test GASPILLOMÈTRE")
parser.add_argument("--test", type=str, default=None, help="Fonction Test")
args = parser.parse_args()

print("Appuyez sur 'q' pour quitter.")

try:
    ajouter_log("Lancement Detection Plateau...")
    while True:
        frame = picam2.capture_array()
        
        # Passer en Gris et augmenter le contraste
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Nettoyer et simplifier
        blur = cv2.medianBlur(gray, 15)
        
        # transformer en noir et blanc
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # detecter les formes geometriques
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            un_pour_cent = 1333.33
            
            # Occuper au moins 35% de l'image
            if area > un_pour_cent * 35:
                # Calcul de la solidité : Aire du contour / Aire de l'enveloppe convexe
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area)/hull_area if hull_area > 0 else 0
                
                # Un rectangle (même arrondi) est très "solide" (> 0.9)
                if solidity > 0.9:
                    # On dessine un rectangle englobant (Bounding Box)
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect_ratio = float(w)/h
                    BOOL=True
                    
                    # vérifier que c'est bien une forme allongée (le plateau)
                    if 1.1 < aspect_ratio < 2.2:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
                        cv2.putText(frame, f"PLATEAU ({int(solidity*100)}%)", (x, y-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    BOOL=False

        cv2.imshow("Detection par Solidite", frame)
        
        if BOOL:
            if plateau_deja_vu == False:
                # Choix image test ou temps-réel
                if args.test:
                    print(args.test)
                    filename = args.test
                    delete = False
                else :
                    filename = f"Capture/capture_{num}.jpg"
                    cv2.imwrite(filename, frame)
                    delete = True
                
                # Exécution modèle de reconnaissance des déchet
                print(f"Photo prise : {filename}")
                print("Lancement reconnaissance...")
                ajouter_log("Lancement reconnaissance...")
                cmd = ["python3", "inference.py", "--image", filename, "--conf", "0.75"]
                subprocess.run(cmd)
                
                # Envoi réseau des données en fond vers l'api
                print("Envoi données à l'API...")
                ajouter_log("Envoi données à l'API...")
                thread_api = threading.Thread(
                    target=envoyer_analyse_api, 
                    args=() 
                )
                thread_api.start()
                
                num += 1
                plateau_deja_vu = True
                
                # Suppression de la photo locale
                if delete == True :
                    os.remove(filename)
                
                # Envoi réseau des logs en fond vers l'api
                """
                print("Envoi log à l'API...")
                ajouter_log("Envoi log à l'API...")
                thread_api = threading.Thread(
                    target=envoyer_log_api, 
                    args=() 
                )
                thread_api.start()
                """
        else:
            if plateau_deja_vu == True:
                print("Prêt pour le suivant")
                plateau_deja_vu = False
                print(plateau_deja_vu)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Erreur : {e}")
    

finally:  
    # Fermeture caméra      
    picam2.stop()
    cv2.destroyAllWindows()

