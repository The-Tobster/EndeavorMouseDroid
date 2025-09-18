import socket
import pigpio

# Setup Pi GPIO (example for L298N motor driver)
pi = pigpio.pi()
ENA, IN1, IN2 = 21, 20, 16  # Motor A
ENB, IN3, IN4 = 26, 19, 13  # Motor B

for pin in [IN1, IN2, IN3, IN4]:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin, 0)

for pwm in [ENA, ENB]:
    pi.set_mode(pwm, pigpio.OUTPUT)
    pi.set_PWM_frequency(pwm, 1000)

def set_motor(left, right):
    # left/right: -100 to 100
    def motor(speed, ena, in1, in2):
        if speed >= 0:
            pi.write(in1, 1); pi.write(in2, 0)
        else:
            pi.write(in1, 0); pi.write(in2, 1)
        pi.set_PWM_dutycycle(ena, min(abs(speed),100)*2.55)

    motor(left, ENA, IN1, IN2)
    motor(right, ENB, IN3, IN4)

# Networking
HOST = ''  # listen on all interfaces
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
            set_motor(80, 80)
        elif data == "back":
            set_motor(-80, -80)
        elif data == "left":
            set_motor(-60, 60)
        elif data == "right":
            set_motor(60, -60)
        elif data == "stop":
            set_motor(0, 0)

except KeyboardInterrupt:
    pass

finally:
    conn.close()
    server.close()
    pi.stop()
