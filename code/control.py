import socket
import pigpio

pi = pigpio.pi()
if not pi.connected:
    exit()

# Motor pins (L298N)
ENA, IN1, IN2 = 21, 20, 16

pi.set_mode(IN1, pigpio.OUTPUT)
pi.set_mode(IN2, pigpio.OUTPUT)
pi.set_mode(ENA, pigpio.OUTPUT)
pi.set_PWM_frequency(ENA, 1000)  # 1kHz PWM

# Servo pin
SERVO = 18
pi.set_mode(SERVO, pigpio.OUTPUT)

def set_motor(speed):
    """speed = -100..100"""
    if speed > 0:
        pi.write(IN1, 1)
        pi.write(IN2, 0)
    elif speed < 0:
        pi.write(IN1, 0)
        pi.write(IN2, 1)
    else:
        pi.write(IN1, 0)
        pi.write(IN2, 0)
    pi.set_PWM_dutycycle(ENA, min(abs(speed), 100) * 2.55)

def set_servo(angle):
    """
    angle = -45..45 degrees
    Maps to ~1000–2000 µs pulse
    """
    pulse = 1500 + (angle * 500 // 45)  # center=1500, left=1000, right=2000
    pi.set_servo_pulsewidth(SERVO, pulse)

# Networking setup
HOST = ''  
PORT = 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Waiting for connection...")
conn, addr = server.accept()
print("Connected by", addr)

try:
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        print("Command:", data)

        if data == "forward":
            set_motor(40)
        elif data == "back":
            set_motor(-40)
        elif data == "stop":
            set_motor(0)
        elif data == "left":
            set_servo(-30)
        elif data == "right":
            set_servo(30)
        elif data == "center":
            set_servo(0)
        elif data == "end":
            print("Shutting down control...")
            set_motor(0)
            set_servo(0)
            break

except KeyboardInterrupt:
    pass

finally:
    conn.close()
    server.close()
    pi.set_servo_pulsewidth(SERVO, 0)  # turn off servo PWM
    pi.stop()
