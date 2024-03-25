import bluetooth
import time
import tkinter as tk
from tkinter import scrolledtext

# The address of your Arduino's Bluetooth module. Replace with your module's address.
bd_addr = "58:56:00:00:81:ED" 

port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr, port))

def send_command(command):
    sock.send(command)
    time.sleep(1.3)  # Wait for the command to be executed


# Define the programming language
commands = {
    "move forward": "F",
    "turn left": "L",
    "turn right": "R",
    "move backward": "B",
}

conditions = {
    "always": lambda: True,
    "never": lambda: False,
    # Add more conditions as needed
}

variables = {}

def parse_script(script):
    lines = script.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '=' in line:
            # Variable assignment
            var_name, value = line.split('=')
            variables[var_name.strip()] = value.strip()
        elif line.startswith('for '):
            # Parse the loop syntax: for n
            _, n = line.split(' ', 1)
            loop_lines = []
            i += 1
            while i < len(lines) and lines[i].startswith('    '):  # 4 spaces for indentation
                loop_lines.append(lines[i].strip())
                i += 1
            for _ in range(int(variables.get(n, n))):
                for command in loop_lines:
                    if command in commands:
                        send_command(commands[command])
                        time.sleep(0.3)
            continue
        elif line.startswith('while '):
            # Parse the loop syntax: while condition command
            _, condition, command = line.split(' ', 2)
            while conditions.get(variables.get(condition, condition), lambda: False)():
                if command in commands:
                    send_command(commands[command])
        elif line in commands:
            send_command(commands[line])
        i += 1
        time.sleep(0.5)

root = tk.Tk()

text_box = scrolledtext.ScrolledText(root, width=40, height=10)
text_box.pack()

run_button = tk.Button(root, text="Run", command=lambda: parse_script(text_box.get("1.0", "end-1c")))
run_button.pack()

root.mainloop()

sock.close()