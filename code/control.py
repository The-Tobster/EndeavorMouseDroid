# server_pi.py
import pigpio
import socket

# --- Motor Pins (L298N single channel) ---
ENA = 20   # PWM enable
IN1 = 21   # direction
IN2 = 16   # direction
SERVO = 18 # must support hardware PWM

# --- Setup pigpio ---
pi = pigpio.pi()
if not pi.connected:
    exit("Pigpio not running!")

for pin in [ENA, IN1, IN2]:
    pi.set_mode(pin, pigpio.OUTPUT)

# Setup ENA for PWM (speed control)
pi.set_PWM_frequency(ENA, 1000)  # 1kHz PWM
pi.set_PWM_range(ENA, 100)

# --- Motor control ---
def stop():
    pi.set_PWM_dutycycle(ENA, 0)
    pi.write(IN1, 0)
    pi.write(IN2, 0)

def forward(speed=50):
    pi.write(IN1, 1)
    pi.write(IN2, 0)
    pi.set_PWM_dutycycle(ENA, speed)  # % duty cycle (0–100)

def backward(speed=50):
    pi.write(IN1, 0)
    pi.write(IN2, 1)
    pi.set_PWM_dutycycle(ENA, speed)

# --- Servo control ---
def set_servo(angle):
    """Set servo instantly to angle (-45 to +45)."""
    pulse = 1500 + (angle * 500 // 45)  # map angle → µs
    pi.set_servo_pulsewidth(SERVO, pulse)

# --- Network Server ---
HOST = " "
PORT = 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Waiting for client...")

conn, addr = server.accept()
print(f"Connected to {addr}")

try:
    set_servo(0)  # center steering
    while True:
        data = conn.recv(1)
        if not data:
            break
        key = data.decode("utf-8").lower()

        if key == "w":
            forward(50)   # 50% speed forward
        elif key == "s":
            backward(50)  # 50% speed backward
        elif key == "a":
            set_servo(-30)  # turn left
        elif key == "d":
            set_servo(30)   # turn right
        elif key == " ":
            stop()
            set_servo(0)   # center steering
        elif key == "q":
            stop()
            set_servo(0)
            break
finally:
    stop()
    pi.set_servo_pulsewidth(SERVO, 0)  # release servo
    pi.stop()
    conn.close()
    server.close()
    print("Server closed")
