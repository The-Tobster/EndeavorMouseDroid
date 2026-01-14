import subprocess
import sys
import time

# Define the scripts to run
script1 = 'subproces/Camera_Stream.py'
script2 = 'subproces/control.py'

print(f"Starting {script1} and {script2} concurrently...")

# Start the processes without waiting
process1 = subprocess.Popen([sys.executable, script1])
process2 = subprocess.Popen([sys.executable, script2])

print("Both processes started. Main program continuing...")

# Optional: Wait for both processes to complete before the main program finishes
process1.wait()
process2.wait()
print("Both concurrent scripts have finished.")
