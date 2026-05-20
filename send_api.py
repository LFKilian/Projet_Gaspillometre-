import requests
from datetime import datetime
import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
token = "J1Yz5Ic6Ht+koGlVOukLeQ$gF75BH8vAEX3NrEvy/OV5KzvcJSIYcAYUh/vSbQ5Gkk"
rasp_id="rasp1"
RESULTS_DIR = PROJECT_ROOT / "Final" / "results"
LOGS_DIR = PROJECT_ROOT / "Final" / "logs"
path_json = RESULTS_DIR / "resultats.jsonl"
path_log = LOGS_DIR / "logs.jsonl"

def envoyer_analyse_api():

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
   
    nouvelle_ligne = {
        "timestamp": date_actuelle,
        "message": str(message)
    }
    
    with open(path_log, 'a', encoding='utf-8') as f:
        f.write(json.dumps(nouvelle_ligne, ensure_ascii=False) + '\n') 

"""
def envoyer_log_api():

    url = "http://10.0.200.78:8000/SendLog"

    if not os.path.exists(path_log):
        print(f"Erreur : {path_log} introuvable")
        return
    
    try:
        # Lecture et chargement du fichier JSON
        with open(path_log, 'r', encoding='utf-8') as f:
            for ligne in f:
                donnees_json = json.loads(ligne)

                actions = donnees_json.get('message')
                if actions:
                    actions_log.append(actions)

                for log in actions_logs:
                
                    # Paramètres FastAPI
                    parametres = {
                        "date": str(date_actuelle),
                        "message": str(log),
                        "rasp": str(rasp_id),
                        "token": str(token)
                    }
                    
                    # Envoi
                    response = requests.post(url, params=parametres, timeout=5)
                    if response.status_code in [200, 201]:
                        print(f"API : Succès !")
                    else:
                        print(f"API : Erreur {response.status_code} : {response.text}")
                        
        if succes == True:
            os.remove(path_json)
            print(f"API : Succès !")
            ajouter_log("API : Succès !")                

    except Exception as e:
        print(f"API : Échec de la connexion : {e}") """
