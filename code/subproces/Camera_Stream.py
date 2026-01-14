from flask import Flask, Response
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import threading
import io
import time

app = Flask(__name__)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

output = StreamingOutput()

picam2 = Picamera2()

# Configure camera
config = picam2.create_video_configuration(
    sensor={"output_size": (3280, 2464)},
    main={"size": (640, 480), "format": "RGB888"},
    controls={"FrameRate": 30}
)
picam2.configure(config)

encoder = MJPEGEncoder(bitrate=10_000_000)
picam2.start_recording(encoder, FileOutput(output))

def generate_frames():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
