import time
from sts3215 import ST3215


ruka = ST3215()


zadnja_pozicija = None

def pomak(id1, id2, id3, id4, id5, gripper):
    """
    Šalje ruku i gripper direktno na zadane korake.
    Brzina, ubrzanje i tajming se računaju automatski za svih 6 motora.
    """
    global zadnja_pozicija
    
    BRZINA_KRETANJA = 700 
    UBRZANJE_ZALETA = 50  
    
    nova_pozicija = [id1, id2, id3, id4, id5, gripper]
    
    
    if zadnja_pozicija is None:
        stvarno_stanje = []
        for servo_id in range(1, 7):
            poz = ruka.read_position(servo_id)
            if poz is None:
                poz = nova_pozicija[servo_id - 1] 
            stvarno_stanje.append(poz)
            time.sleep(0.002)
        zadnja_pozicija = stvarno_stanje
    
    
    najveci_put = 0
    for stari, novi in zip(zadnja_pozicija, nova_pozicija):
        razlika = abs(novi - stari)
        if razlika > najveci_put:
            najveci_put = razlika
            
   
    slanje = []
    for i, kut in enumerate(nova_pozicija, 1):
        slanje.append({
            "id": i, 
            "pos": kut, 
            "acc": UBRZANJE_ZALETA, 
            "speed": BRZINA_KRETANJA
        })
        
    ruka.write_synchronous(slanje)
    
    
    if najveci_put > 0:
        potrebno_vrijeme = (najveci_put / BRZINA_KRETANJA) + 0.05
    else:
        potrebno_vrijeme = 0.01
        
    if potrebno_vrijeme < 0.05:
        potrebno_vrijeme = 0.05
        
    time.sleep(potrebno_vrijeme)
    zadnja_pozicija = nova_pozicija

try:
    print("Pokrećem sekvencu ruke i hvataljke...")

    # ==============================================================
    
    pomak(1867, 1645, 1944, 2456, 2963, 2420)
    pomak(2339, 2475, 1998, 1243, 2963, 2420)
    pomak(1608, 2372, 1726, 2328, 2962, 2128)
    pomak(2884, 1712, 1365, 2042, 2960, 2128)
    pomak(2789, 2608, 1696, 2474, 2959, 2129)
    pomak(2077, 2206, 1701, 2474, 2961, 2125)
    pomak(2076, 1467, 2591, 1826, 2962, 2125)
    pomak(2077, 862, 3044, 896, 2959, 2125)
    
    # =================================================================

    print("Sve pozicije (uključujući gripper) su uspješno odrađene!")

except Exception as e:
    print(f"Došlo je do greške: {e}")
finally:
    ruka.close()
    print("Komunikacija zatvorena.")
