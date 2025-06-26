# microbit_receiver.py
from microbit import *

# Initialize serial communication
uart.init(baudrate=9600)

display.show(Image.ASLEEP) # Show sleeping icon on startup

while True:
    if uart.any():
        command = uart.readline().strip()
        
        if command == b'FACE1':
            display.show("1")
        elif command == b'FACE2':
            display.show("2")
        elif command == b'UNKNOWN':
            display.show(Image.SKULL)
        else:
            display.show("?")

    sleep(100)
