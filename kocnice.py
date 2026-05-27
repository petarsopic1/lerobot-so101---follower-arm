import time
from sts3215 import ST3215

try:
    
    ruka = ST3215()
    
    
    for servo_id in range(1, 7):
        ruka.set_torque(servo_id, False)
        time.sleep(0.005) 
        
    print("Kočnice uspješno ugašene. Ruka je slobodna za micanje!")

except Exception as e:
    print(f"Greška pri gašenju kočnica: {e}")
finally:
  
    if 'ruka' in locals():
        ruka.close()
