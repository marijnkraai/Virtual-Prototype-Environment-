import time
import serial
from serial_config import SERIALPORTGCODE, BAUDRATE
import threading
from collections import deque

conn = None
           
def setupMachine(conn):
    print("SETTING UP MACHINE")
    sendGRBL("?", conn)   # Fetch device status
    sendGRBL("$$", conn)   # Fetch device version
    homeMachine(conn)
    sendGRBL("$X", conn)  # Unlock the machines
    sendGRBL("G10 L20 P1 X0 Y0 Z0", conn)
    print("DONE SETUP UP MACHINE")

def MoveToPosition(x, y, conn):
    # Send the G0 command to move to the desired position
    print(f"Moving to position X{x}, Y{y}...")
    command = f"G0 F5000 X{x} Y{y}"
    sendGRBL(command, conn)
    time.sleep(0.1)
    #while True:
        #response = sendGRBL("?", conn)
        #print(response)
        #if "Idle" in response:
            #print("Movement complete")
            #return
        
        #status = conn.readline().decode().strip()
        #print(status)
        
def sendGRBL(grbl_command, conn):
    """Send a command to GRBL and read the response."""
    print(f"sending commmand {grbl_command}")
    conn.write(f"{grbl_command}\n".encode())  # Send command
    time.sleep(0.1)  # Short delay to allow GRBL to process
    while True:
        response = conn.readline().decode().strip()
        if response:
            return response
    
def homeMachine(conn):
    sendGRBL("$H", conn)
    print("Homing command sent. Waiting for homing to complete...")
    while True:
        status = conn.readline().decode().strip()
        print(status)
        if "ok" in status:
            print("Homing complete.")
            return



def createSerialConnection(serialPort, baudRate):
    ser = None
    try:
        ser = serial.Serial(serialPort, baudRate, timeout=1) 
        print(f"Successfully connected to {serialPort} at {baudRate} baud.")
        return ser

    except serial.SerialException as e:
        print(f"Serial error: {e}")  # Print error message if COM port cannot be opened
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if ser is not None and not ser.is_open:
            try:
                ser.close()  # Ensure that the serial port is closed properly
            except Exception as e:
                print(f"Error closing serial port: {e}")


def main():
    global conn
    conn = createSerialConnection(SERIALPORTGCODE, BAUDRATE)
    setupMachine(conn)
    MoveToPosition(400,400, conn)
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    main()

