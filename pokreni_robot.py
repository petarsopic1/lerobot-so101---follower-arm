import time
import sys
import json
import os
from sts3215 import ST3215

PLAN_PATH = "/home/pi/robot/plan_gibanja.json"

if not os.path.exists(PLAN_PATH):
    sys.stderr.write("Greška: Datoteka plan_gibanja.json ne postoji!\n")
    sys.exit(1)

try:
    # 1. Čitamo plan koji je Node-RED zapisao (tvoje točke, brzinu i ubrzanje)
    with open(PLAN_PATH, "r") as f:
        podaci = json.load(f)
    
    # Ako klizači nisu dirani, uzimamo tvoje zadane vrijednosti iz pomakni.py (700 i 50)
    brzina_klizaca = podaci.get("brzina", 700)
    ubrzanje_klizaca = podaci.get("ubrzanje", 50)
    tocke = podaci.get("tocke", [])
    
    if not tocke:
        sys.stderr.write("Greška: Nema snimljenih točaka u planu!\n")
        sys.exit(1)
        
    # 2. Spajanje na robota
    ruka = ST3215()
    time.sleep(0.1)  # Stabilizacija porta
    
    print(f"Pokrećem sinkronu sekvencu od {len(tocke)} točaka.")
    print(f"Brzina s tableta: {brzina_klizaca} | Ubrzanje s tableta: {ubrzanje_klizaca}")
    
    # Krećemo od prve točke, a u petlji ćemo pratiti zadnju poziciju za proračun tajminga
    zadnja_pozicija = None
    
    # 3. Prolazimo kroz sve snimljene točke
    for i, tocka in enumerate(tocke):
        print(f"Idem na točku {i + 1}: {tocka}")
        
        # Ako nemamo zadnju poziciju (prva točka), očitaj stvarno stanje s robota radi glatkog starta
        if zadnja_pozicija is None:
            stvarno_stanje = []
            for servo_id in range(1, 7):
                poz = ruka.read_position(servo_id)
                if poz is None:
                    poz = tocka[servo_id - 1]
                stvarno_stanje.append(poz)
                time.sleep(0.002)
            zadnja_pozicija = stvarno_stanje

        # Tražimo najveći put među svih 6 motora za pametnu pauzu
        najveci_put = 0
        for stari, novi in zip(zadnja_pozicija, tocka):
            razlika = abs(novi - stari)
            if razlika > najveci_put:
                najveci_put = razlika

        # Pakiramo podatke točno onako kako write_synchronous traži
        paket_za_slanje = []
        for indeks, kut in enumerate(tocka, 1):
            paket_za_slanje.append({
                "id": indeks,
                "pos": kut,
                "acc": ubrzanje_klizaca,
                "speed": brzina_klizaca
            })
            
        # ŠALJEMO SVIH 6 MOTORIMA ODJEDNOM!
        ruka.write_synchronous(paket_za_slanje)
        
        # Računamo koliko točno moramo čekati da ruka stigne u točku
        if najveci_put > 0:
            potrebno_vrijeme = (najveci_put / brzina_klizaca) + 0.15 # Dodano malo lufta za sigurnost
        else:
            potrebno_vrijeme = 0.05
            
        if potrebno_vrijeme < 0.2:
            potrebno_vrijeme = 0.2
            
        time.sleep(potrebno_vrijeme)
        zadnja_pozicija = tocka
        
    print("Sekvenca uspješno završena! Svi motori su odradili svoje.")

except Exception as e:
    sys.stderr.write(f"Greška tijekom izvođenja: {e}\n")
finally:
    if 'ruka' in locals():
        ruka.close()