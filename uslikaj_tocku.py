import time
import sys
import os


sys.stdout = open(os.devnull, 'w')
from sts3215 import ST3215

sys.stdout = sys.__stdout__

try:
    ruka = ST3215()
    time.sleep(0.05) 
    
    trenutne_pozicije = []
    
   
    for servo_id in range(1, 7):
        poz = ruka.read_position(servo_id)
        if poz is None:
            poz = 2048
        trenutne_pozicije.append(poz)
        time.sleep(0.005)
        
    
    print(",".join(map(str, trenutne_pozicije)))

except Exception as e:
   
    sys.stderr.write(f"Greska: {e}\n")
finally:
    if 'ruka' in locals():
        ruka.close()
