import socket
import pigpio
import time

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

current_angle = 0  # keep track of where the servo is

def set_servo(target_angle, step=2, delay=0.02):
    """
    Move servo gradually to target_angle
    target_angle: -45..45
    step: how many degrees per update
    delay: pause between updates (seconds)
    """
    global current_angle
    while current_angle != target_angle:
        if current_angle < target_angle:
            current_angle += step
            if current_angle > target_angle:
                current_angle = target_angle
        elif current_angle > target_angle:
            current_angle -= step
            if current_angle < target_angle:
                current_angle = target_angle

        # convert angle to pulse width
        pulse = 1500 + (current_angle * 500 // 45)
        pi.set_servo_pulsewidth(SERVO, pulse)
        time.sleep(delay)

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
            set_servo(-23)
        elif data == "right":
            set_servo(23)
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
