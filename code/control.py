import socket
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Motor pins (L298N)
ENA, IN1, IN2 = 21, 20, 16
GPIO.setup([ENA, IN1, IN2], GPIO.OUT)
motor_pwm = GPIO.PWM(ENA, 1000)  # PWM at 1kHz
motor_pwm.start(0)

# Servo pin
SERVO = 18
GPIO.setup(SERVO, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO, 50)  # 50Hz
servo_pwm.start(0)

# State variables
state = {"forward": False, "backward": False, "left": False, "right": False}

# Helper functions
def set_motor(forward, backward):
    if forward:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        motor_pwm.ChangeDutyCycle(100)  # speed %
    elif backward:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        motor_pwm.ChangeDutyCycle(100)
    else:
        motor_pwm.ChangeDutyCycle(0)

def set_servo(left, right):
    if left:
        servo_pwm.ChangeDutyCycle(6.6)  # adjust for your servo
    elif right:
        servo_pwm.ChangeDutyCycle(8.4)   # adjust for your servo
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

            if data == "w_down":
                state["forward"] = True
            elif data == "w_up":
                state["forward"] = False
            elif data == "s_down":
                state["backward"] = True
            elif data == "s_up":
                state["backward"] = False
            elif data == "a_down":
                state["left"] = True
            elif data == "a_up":
                state["left"] = False
            elif data == "d_down":
                state["right"] = True
            elif data == "d_up":
                state["right"] = False

            # Apply states
            # Forward/backward
            if state["forward"] and not state["backward"]:
                set_motor(TRUE, FALSE)
            elif state["backward"] and not state["forward"]:
                set_motor(FALSE, TRUE)
            else:
                set_motor(FALSE, FALSE)
            
            # Left/right
            if state["left"] and not state["right"]:
                set_servo(TRUE, FALSE)
            elif state["right"] and not state["left"]:
                set_servo(FALSE, TRUE)
            else:
                set_servo(FALSE, FALSE)

    finally:
        motor_pwm.stop()
        servo_pwm.stop()
        GPIO.cleanup()
