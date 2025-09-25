import socket
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Motor pins (L298N)
ENA, IN1, IN2 = 20, 21, 16
GPIO.setup([ENA, IN1, IN2], GPIO.OUT)
motor_pwm = GPIO.PWM(ENA, 1000)  # PWM at 1kHz
motor_pwm.start(0)

# Servo pin
SERVO = 18
GPIO.setup(SERVO, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO, 50)  # 50Hz
servo_pwm.start(0)

# State variables
forward_active = False
backward_active = False
left_active = False
right_active = False

# Helper functions
def set_motor(forward, backward):
    if forward:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        motor_pwm.ChangeDutyCycle(60)  # speed %
    elif backward:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        motor_pwm.ChangeDutyCycle(60)
    else:
        motor_pwm.ChangeDutyCycle(0)

def set_servo(left, right):
    if left:
        servo_pwm.ChangeDutyCycle(10)  # adjust for your servo
    elif right:
        servo_pwm.ChangeDutyCycle(5)   # adjust for your servo
    else:
        servo_pwm.ChangeDutyCycle(7.5) # center

# Networking
HOST = "0.0.0.0"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Waiting for connection...")
    conn, addr = s.accept()
    print(f"Connected by {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()

            if msg == "w_down": forward_active = True
            if msg == "w_up": forward_active = False
            if msg == "s_down": backward_active = True
            if msg == "s_up": backward_active = False
            if msg == "a_down": left_active = True
            if msg == "a_up": left_active = False
            if msg == "d_down": right_active = True
            if msg == "d_up": right_active = False

            # Apply states
            set_motor(forward_active, backward_active)
            set_servo(left_active, right_active)

    finally:
        motor_pwm.stop()
        servo_pwm.stop()
        GPIO.cleanup()
