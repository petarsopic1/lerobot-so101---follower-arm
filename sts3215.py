import time
import serial

class ST3215:
    def __init__(self, port="/dev/ttyACM1", baudrate=1000000):
        
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"Driver: Uspješno spojen na {port}!")
            time.sleep(1)
            return
        except Exception:
            pass

        
        rezervni = "/dev/ttyACM0" if "ACM1" in port else "/dev/ttyACM1"
        try:
            self.ser = serial.Serial(rezervni, baudrate, timeout=1)
            print(f"Driver: {port} nedostupan. Uspješno spojen na rezervni {rezervni}!")
            time.sleep(1)
            return
        except Exception as e:
            print(f"\n[ KRAH DRIVERA ] Nemoguće otvoriti niti jedan USB port (/dev/ttyACM1 ili /dev/ttyACM0)!")
            print("Provjeri je li USB kabel fizički ukopčan u Raspberry Pi.")
            raise e

    def write_synchronous(self, position_speed_list):
        data_length = 6 
        packet_len = (data_length + 1) * len(position_speed_list) + 4
        frame = [0xFF, 0xFF, 0xFE, packet_len, 0x83, 0x2A, data_length]
        
        for servo in position_speed_list:
            srv_id = servo["id"]
            pos = int(servo["pos"])
            acc = int(servo["acc"])   
            spd = int(servo["speed"]) 
            
            pos_l = pos & 0xFF
            pos_h = (pos >> 8) & 0xFF
            acc_l = acc & 0xFF
            acc_h = (acc >> 8) & 0xFF
            spd_l = spd & 0xFF
            spd_h = (spd >> 8) & 0xFF
            
            frame.extend([srv_id, pos_l, pos_h, acc_l, acc_h, spd_l, spd_h])
            
        checksum = ~sum(frame[2:]) & 0xFF
        frame.append(checksum)
        self.ser.write(bytearray(frame))

    def set_torque(self, servo_id, enable):
        value = 1 if enable else 0
        frame = [0xFF, 0xFF, servo_id, 0x04, 0x03, 0x28, value]
        checksum = ~sum(frame[2:]) & 0xFF
        frame.append(checksum)
        self.ser.write(bytearray(frame))
        time.sleep(0.005)

    def read_position(self, servo_id):
        self.ser.reset_input_buffer()
        frame = [0xFF, 0xFF, servo_id, 0x04, 0x02, 0x38, 0x02]
        checksum = ~sum(frame[2:]) & 0xFF
        frame.append(checksum)
        
        self.ser.write(bytearray(frame))
        response = self.ser.read(8)
        if len(response) == 8 and response[0] == 0xFF and response[1] == 0xFF:
            pos_l = response[5]
            pos_h = response[6]
            return (pos_h << 8) | pos_l
        return None

    def close(self):
        self.ser.close()
