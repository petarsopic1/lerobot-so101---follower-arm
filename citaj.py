import time
from sts3215 import ST3215


ruka = ST3215()

print("--- SNIMANJE CIJELE SEKVENCE NA TIPKU ---")
print("Gasim torque na svim motorima... Ruka je slobodna!")
print("\nUPUTE:")
print("1. Fizički namjesti ruku i gripper u željeni položaj.")
print("2. Stisni [ ENTER ] da privremeno snimiš tu točku.")
print("3. Kad završiš cijelu putanju, upiši [ q ] i stisni Enter.")
print("-" * 50 + "\n")


for servo_id in range(1, 7):
    ruka.set_torque(servo_id, enable=False)

brojac_pozicija = 1
lista_snimljenih_linija = []

try:
    while True:
        unos = input(f"Postavi poziciju {brojac_pozicija} i stisni ENTER (ili 'q' za kraj): ")
        
        if unos.strip().lower() == 'q':
            break
            
        trenutni_koraci = []
        greska = False
        
        for servo_id in range(1, 7):
            pozicija = ruka.read_position(servo_id)
            if pozicija is not None:
                trenutni_koraci.append(pozicija)
            else:
                greska = True
                break
            time.sleep(0.005)
            
        if not greska and len(trenutni_koraci) == 6:
            formatirana_linija = f"    pomak({trenutni_koraci[0]}, {trenutni_koraci[1]}, {trenutni_koraci[2]}, {trenutni_koraci[3]}, {trenutni_koraci[4]}, {trenutni_koraci[5]})"
            lista_snimljenih_linija.append(formatirana_linija)
            print(f"-> Točka {brojac_pozicija} uspješno spremljena u memoriju.\n")
            brojac_pozicija += 1
        else:
            print("\n[ GREŠKA ] Ne mogu pročitati motore. Pokušaj ponovo.\n")

except KeyboardInterrupt:
    pass

finally:
    print("\n" + "="*60)
    print(" REZULTAT SNIMANJA (Kopiraj sve odjednom ispod ove linije):")
    print("="*60 + "\n")
    
    if lista_snimljenih_linija:
        for linija in lista_snimljenih_linija:
            print(linija)
    else:
        print("    # Nisi snimio nijednu poziciju.")
        
    print("\n" + "="*60)
    print("Vraćam kočnice (Torque ON)...")
    
    for servo_id in range(1, 7):
        try:
            ruka.set_torque(servo_id, enable=True)
        except Exception:
            pass
    ruka.close()
    print("Sustav osiguran. Veza zatvorena.")
