import time
from sts3215 import ST3215

try:
    # Spajamo se na driver robota
    ruka = ST3215()
    
    # Gasimo torque (kočnice) za svih 6 motora da ruka postane mlohava
    for servo_id in range(1, 7):
        ruka.set_torque(servo_id, False)
        time.sleep(0.005) # Mala pauza između motora za stabilnost komunikacije
        
    print("Kočnice uspješno ugašene. Ruka je slobodna za micanje!")

except Exception as e:
    print(f"Greška pri gašenju kočnica: {e}")
finally:
    # Obavezno zatvaramo port da ne ostane zaključan!
    if 'ruka' in locals():
        ruka.close()