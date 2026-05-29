import requests
from datetime import datetime
import os
import json
from pathlib import Path
import sys
import logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent
date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
pass_token = "b8c95e1a-18a6-11f1-a5d2-423b83e4d33c"
rasp_id="rasp1"
RESULTS_DIR = PROJECT_ROOT / "Final" / "results"
LOGS_DIR = PROJECT_ROOT / "Final" / "logs"
path_json = RESULTS_DIR / "resultats.jsonl"
path_log = LOGS_DIR / "logs.log"
path_log_save = LOGS_DIR / "save_log.log"


format_log = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# Le fichier temporaire
handler_tmp = logging.FileHandler(path_log, mode='w', encoding='utf-8')
handler_tmp.setFormatter(format_log)
# Le fichier de sauvegarde historique
handler_save = logging.FileHandler(path_log_save, mode='a', encoding='utf-8')
handler_save.setFormatter(format_log)
# On applique la configuration au système de log de Python
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler_tmp)
logger.addHandler(handler_save)

def getToken():
    url = "http://10.0.200.78:8000/token"
    
    parametres = {
        "username": str(rasp_id),
        "password": pass_token
        }
        
    response = requests.post(url, data=parametres, timeout=5)
    
    if response.status_code in [200, 201]:
        donnees = response.json()
        token_extrait = donnees.get("access_token")
        return token_extrait
    else:
        print(f"API : Erreur {response.status_code} : {response.text}")

token = getToken()            
print(token)

def envoyer_analyse_api():

    retries = 0
    url = "http://10.0.200.78:8000/insertAnalyse"

    # Vérification que le fichier JSON existe bien
    if not os.path.exists(path_json):
        print(f"Erreur : {path_json} introuvable")
        return

    try:
        # Lecture et chargement du fichier JSON
        with open(path_json, 'r', encoding='utf-8') as f:
            for ligne in f:
                if ligne.strip():
                    donnees_json = json.loads(ligne)

                    # Extraction
                    type_dechet = donnees_json.get("class_id")
                    poid = donnees_json.get("weight_g")   
                    
                    if type_dechet is None:
                        type_dechet=int(0)
                    if poid is None:
                        poid=int(0)
                    
                    # Paramètres FastAPI
                    parametres = {
                        "date": str(date_actuelle),
                        "type_dechet": int(type_dechet),
                        "poid": float(poid),
                        "rasp": str(rasp_id),
                        "token": str(token)
                    }
                    
                    # Envoi
                    response = requests.post(url, params=parametres, timeout=5)
                    if response.status_code in [200, 201]:
                        succes = True
                    if response.status_code in [401]:
                        print(f"Erreur {response.status_code}")
                        token = getToken()
                        succes = False
                        envoyer_analyse_api()
                    else:
                        print(f"API : Erreur {response.status_code} : {response.text}")
                        ajouter_log(f"API : Erreur {response.status_code} : {response.text}")
                        succes = False
                
        if succes == True:
            os.remove(path_json)
            print(f"API : Succès !")
            ajouter_log("API : Succès !")
            
    except Exception as e:
        print(f"API : Échec de la connexion : {e}")
        ajouter_log(f"API : Échec de la connexion : {e}")


def ajouter_log(message):
   logging.info(message)


def envoyer_log_api():
    
    global token
    url = "http://10.0.200.78:8000/insertLog"

    if not os.path.exists(path_log):
        print(f"Erreur : {path_log} introuvable")
        return
    
    try:
        # Lecture et chargement du fichier JSON
        with open(path_log, 'r', encoding='utf-8') as f:
            ligne = f.read().strip()

        if ligne:
            extrait = ligne.split("|")
            date_extrait = extrait[0].strip()
            level_extrait = extrait[1].strip()
            message_extrait = extrait[2].strip()
                
                
            print(token)
            # Paramètres FastAPI
            parametres = {
                "date": str(date_extrait),
                "level": str(level_extrait),
                "message": str(message_extrait),
                "rasp": str(rasp_id),
                "token": str(token)
            }
            
                    
            # Envoi
            response = requests.post(url, params=parametres, timeout=5)
            if response.status_code in [200, 201]:
                print(f"API : Succès !")
            if response.status_code in [401]:
                print(f"Erreur {response.status_code}")
                token = getToken()
                succes = False
                envoyer_analyse_api()
            else:
                print(f"API : Erreur {response.status_code} : {response.text}")
                        

    except Exception as e:
        print(f"API : Échec de la connexion : {e}")

