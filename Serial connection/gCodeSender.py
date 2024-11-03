import time
import serial
from serial_config import SERIALPORTGCODE, BAUDRATE
import threading
from collections import deque

speed = 1.4/(5000/60)
command_queue = deque()
conn = None

# Movement status
is_moving = False

def read_from_grbl(ser):
    global is_moving
    while True:
        response = ser.readline().decode().strip()
        print(f"Received: {response}")
        # Check if the response indicates movement is complete
        if response.startswith("<Idle"):
            is_moving = False  # Movement is complete
            print("Movement finished.")
            execute_next_command()  # Trigger next command in the queue
    #elif response == "ok":
        #print("Command executed successfully.")
            

def execute_next_command():
    global is_moving
    if command_queue:
        next_command = command_queue.popleft()  # Get the next command from the queue
        is_moving = True
        sendGRBL(next_command)
           
def setupMachine():
    sendGRBL("?")   # Fetch device status
    sendGRBL("?")   # Fetch device status
    sendGRBL("$$")   # Fetch device version
    sendGRBL("?")   # Fetch device status
    homeMachine()
    sendGRBL("$X")  # Unlock the machines
    sendGRBL("?")   # Fetch device status
    sendGRBL("G10 L20 P1 X0 Y0 Z0")
    sendGRBL("?")   # Fetch device status
    print("DONE SETUP UP MACHINE")

def MoveToPosition(x, y, callback = None):
    global is_moving
    # Send the G0 command to move to the desired position
    print(f"Moving to position X{x}, Y{y}...")
    command = f"G0 F5000 X{x} Y{y}"
    command_queue.append(command)  # Add command to the queue
    print(f"Queued command: {command}")

    # If not currently moving, execute the next command
    if not is_moving:
        execute_next_command()

def sendGRBL(grbl_command):
    """Send a command to GRBL and read the response."""
    conn.write(f"{grbl_command}\n".encode())  # Send command
    time.sleep(0.1)  # Short delay to allow GRBL to process
    response = conn.readline().decode().strip()
    #print(f"Sent: {grbl_command} | Response: {response}")
    return response
    
def homeMachine():
    response = sendGRBL("$H")
    print("Homing command sent. Waiting for homing to complete...")
    while True:
        status = sendGRBL("?")
        if "Home" in status:
            print("Homing complete.")
            break
        time.sleep(0.5)  # Check status every half second

def movement_finished(success):
    if success:
        print("Callback: Movement completed successfully.")
    else:
        print("Callback: Movement did not complete successfully.")
    
def main():
    global conn
    ser = None
    try:
        with serial.Serial(SERIALPORTGCODE, BAUDRATE, timeout=1) as ser:
            conn = ser
            print(f"Successfully connected to {SERIALPORTGCODE} at {BAUDRATE} baud.")
            listener_thread = threading.Thread(target=read_from_grbl, args=(ser,))
            listener_thread.daemon = True  # Allow thread to exit when the main program does
            listener_thread.start()

            setupMachine()

            MoveToPosition(100,100, movement_finished)
            MoveToPosition(500,500, movement_finished)
            MoveToPosition(300,300, movement_finished)
        
            # Keep the main thread alive to allow for continuous reading
            while True:
                time.sleep(1)

    except serial.SerialException as e:
        print(f"Serial error: {e}")  # Print error message if COM port cannot be opened
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if ser is not None:
            try:
                ser.close()  # Ensure that the serial port is closed properly
            except Exception as e:
                print(f"Error closing serial port: {e}")

if __name__ == "__main__":
    main()

