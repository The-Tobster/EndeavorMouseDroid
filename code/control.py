import socket
import RPi.GPIO as GPIO
import time
import json
from picamera2 import Picamera2, Preview

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
def set_motor(speed):
    if speed>0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        motor_pwm.ChangeDutyCycle(abs(speed))  # speed %
    elif speed<0:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        motor_pwm.ChangeDutyCycle(abs(speed))
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        motor_pwm.ChangeDutyCycle(abs(speed))

def set_servo(angle):
    if angle>0:
        servo_pwm.ChangeDutyCycle(7.5-angle/32)  # adjust for your servo
    elif angle<0:
        servo_pwm.ChangeDutyCycle(7.5-angle/32)   # adjust for your servo
    else:
        servo_pwm.ChangeDutyCycle(7.5-angle/32) # center

# Networking
HOST = "0.0.0.0"
PORT = 65432

# camera start
picam2 = Picamera2()
picam2.set_controls({"ScalerCrop": (0, 0, 1920, 1080)})
config = picam2.create_preview_configuration(
    main={"size": (160, 120)}
)
picam2.configure(config)
picam2.start_preview(Preview.QTGL)
picam2.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Waiting for connection...")
    conn, addr = s.accept()
    print(f"Connected by {addr}")

    try:
        while True:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                break
            msg = json.loads(data)

            set_motor(msg[0])
            set_servo(msg[1])
            
            frame = picam2.capture_array()
        
            # Display the frame
            cv2.imshow("Camera Preview", frame)

    finally:
        motor_pwm.stop()
        servo_pwm.stop()
        GPIO.cleanup()
        picam2.stop()
        cv2.destroyAllWindows()
