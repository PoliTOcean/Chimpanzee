import serial
import threading
import sys
import termios
import tty

# Open serial port
ser = serial.Serial('/dev/cu.usbmodem1303', 115200, timeout=1)  # Adjust port and baudrate as needed

# Messages to send, automatically add CRC and endByte
message1 = [0xFF, 0x00, 0x01, 0x00, 0x01]
message2 = [0xAA, 0x00, 0x00, 0x06, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
message3 = [0xAA, 0x00, 0x00, 0x06, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
message4 = [0xAA, 0x00, 0x00, 0x06, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

def crc8(data):
    crc = 0x00  # Initial value
    poly = 0x07  # CRC-8 polynomial (x^8 + x^2 + x^1 + 1)

    for byte in data:
        crc ^= byte  # XOR-in the next byte
        for _ in range(8):  # Process each bit
            if crc & 0x80:  # If the highest bit is set
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFF  # Ensure CRC remains 8-bit

    return crc

endByte = 0xEE
result = crc8(message1)
message1.append(result)
message1.append(endByte)
result = crc8(message2)
message2.append(result)
message2.append(endByte)
result = crc8(message3)
message3.append(result)
message3.append(endByte)
result = crc8(message4)
message4.append(result)
message4.append(endByte)


# Function to read input without blocking
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def read_serial():
    buffer = bytearray()  # Buffer to store incoming bytes
    while True:
        if ser.in_waiting > 0:
            # Read incoming bytes
            data = ser.read(ser.in_waiting)
            for byte in data:
                buffer.append(byte)
                if byte == 0xEE:  # Trigger condition
                    print(f"Received buffer: {[hex(b) for b in buffer]}\r")
                    buffer.clear()  # Clear buffer after processing

# Start the serial reading thread
reader_thread = threading.Thread(target=read_serial, daemon=True)
reader_thread.start()

# Main loop to send messages based on key presses
print("Press '1' to send Message 1, '2' to send Message 2. Press 'q' to quit.")
try:
    while True:
        key = getch()
        if key == '1':
            for byte in message1:
                ser.write(byte.to_bytes(1, 'big'))  # Convert integer to single byte
                print(f"Sent byte: {hex(byte)}")
        elif key == '2':
            for byte in message2:
                ser.write(byte.to_bytes(1, 'big'))  # Convert integer to single byte
                print(f"Sent byte: {hex(byte)}")
        elif key == '3':
            for byte in message3:
                ser.write(byte.to_bytes(1, 'big'))  # Convert integer to single byte
                print(f"Sent byte: {hex(byte)}")
        elif key == '4':
            for byte in message4:
                ser.write(byte.to_bytes(1, 'big'))  # Convert integer to single byte
                print(f"Sent byte: {hex(byte)}")
        elif key == 'q':  # Quit
            print("Exiting...")
            break
except KeyboardInterrupt:
    print("\nExiting...")

# Close the serial port
ser.close()
