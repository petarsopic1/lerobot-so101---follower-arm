import time
import sys
import os

# Triki korak: Prisilno gasimo standardni ispis (stdout) za driver 
# kako nam rečenica "Driver: /dev/ttyACM1 nedostupan..." ne bi zagađivala podatke.
# Blokiramo ispis dok se driver učitava:
sys.stdout = open(os.devnull, 'w')
from sts3215 import ST3215
# Vraćamo standardni ispis natrag u normalu odmah nakon uvoza drivera:
sys.stdout = sys.__stdout__

try:
    ruka = ST3215()
    time.sleep(0.05) # Kratka pauza za stabilizaciju
    
    trenutne_pozicije = []
    
    # Čitamo redom motore od 1 do 6
    for servo_id in range(1, 7):
        poz = ruka.read_position(servo_id)
        if poz is None:
            poz = 2048
        trenutne_pozicije.append(poz)
        time.sleep(0.005)
        
    # ISPISUJEMO SAMO BROJEVE I NIŠTA DRUGO:
    # Ovo će Node-RED primiti u obliku: 1917,861,3045,886,2957,2127
    print(",".join(map(str, trenutne_pozicije)))

except Exception as e:
    # Greške šaljemo na skriveni stderr kanal da ne smetaju glavnom ispisu
    sys.stderr.write(f"Greska: {e}\n")
finally:
    if 'ruka' in locals():
        ruka.close()