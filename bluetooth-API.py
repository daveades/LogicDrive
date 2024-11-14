from flask import Flask, request, jsonify
import bluetooth
import time

app = Flask(__name__)

# Replace with your Arduino's Bluetooth module address.
bd_addr = "58:56:00:00:81:ED"
port = 1

# Initialize Bluetooth connection
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr, port))

# Define the commands and conditions
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

def send_command(command):
    """Send a command via Bluetooth."""
    sock.send(command)
    time.sleep(1.3)  # Wait for the command to be executed

def parse_script(script):
    """Parse and execute the script commands."""
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

@app.route('/send-command', methods=['POST'])
def send_command_endpoint():
    """Endpoint to send a single command."""
    command_name = request.json.get('command')
    if command_name in commands:
        send_command(commands[command_name])
        return jsonify({"status": "success", "message": f"Command '{command_name}' sent."})
    else:
        return jsonify({"status": "error", "message": "Invalid command"}), 400

@app.route('/execute-script', methods=['POST'])
def execute_script_endpoint():
    """Endpoint to execute a series of commands from a script."""
    script = request.json.get('script')
    try:
        parse_script(script)
        return jsonify({"status": "success", "message": "Script executed successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect_bluetooth():
    """Endpoint to close the Bluetooth connection."""
    try:
        sock.close()
        return jsonify({"status": "success", "message": "Bluetooth connection closed."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

