import cv2
import time
from mtcnn.mtcnn import MTCNN
import serial
import serial.tools.list_ports

# Configuration
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600

# --- Arduino Connection Setup ---
arduino = None

def connect_arduino():
    global arduino
    try:
        # Check if port exists (optional, but good for debugging)
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if SERIAL_PORT not in ports:
            print(f"Warning: {SERIAL_PORT} not found in available ports: {ports}")
            raise serial.SerialException("Port not found")

        arduino = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=.1)
        print(f"Successfully connected to Arduino on {SERIAL_PORT}")
        
    except (serial.SerialException, ImportError, Exception) as e:
        print(f"Arduino connection failed: {e}")
        print("Starting in SIMULATION MODE. No hardware required.")
        
        class MockArduino:
            def write(self, x):
                # Using print for simulation feedback occasionally
                # print(f"[SIMULATION] Sending to Arduino: {x}")
                pass
            def flushInput(self): 
                pass
        
        arduino = MockArduino()

connect_arduino()

# --- Main Logic ---

def main():
    # Initialize Camera
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("Error: Could not open video source.")
        return

    # Initialize Face Detector
    detector = MTCNN()
    
    print("Starting Main Loop. Press 'q' to quit.")

    while True:
        ret, frame = video.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Detect faces
        try:
            faces = detector.detect_faces(frame)
        except Exception as e:
            print(f"Detection error: {e}")
            faces = []

        total_count = len(faces)
        
        # Prepare data for Arduino
        if total_count > 1:
            fdata = "Detected"
        else:
            fdata = "No"
            
        # Send to Arduino (or Mock)
        try:
            arduino.write(str(fdata).encode('utf-8'))
        except Exception as e:
            print(f"Serial write error: {e}")

        # Draw Interface
        for result in faces:
            x, y, w, h = result['box']
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Draw count text
            cv2.putText(frame, f'Count: {total_count}', 
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display Status on Screen (Simulation Feedback)
        status_color = (0, 0, 255) if total_count > 1 else (0, 255, 0)
        cv2.putText(frame, f"Status: {fdata}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        cv2.imshow('Face Count Alert', frame)
        
        # Arduino flush (handled in loop in original code, keeping it)
        try:
            arduino.flushInput()
        except:
            pass

        # Controls
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

    # Cleanup
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
