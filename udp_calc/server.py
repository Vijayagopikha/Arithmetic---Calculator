from flask import Flask, request, jsonify, render_template
import socket
import threading

app = Flask(__name__)

# UDP server settings
udp_address = ('127.0.0.1', 8000)

# Function to perform the arithmetic operation
def calculation(n1, n2, o):
    try:
        if o == '+':
            return n1 + n2
        elif o == '-':
            return n1 - n2
        elif o == '*':
            return n1 * n2
        elif o == '/':
            if n2 == 0:
                raise ValueError("Cannot divide by zero")
            return n1 / n2
        elif o == '%':
            return n1 % n2
        else:
            raise ValueError("Invalid operator")
    except Exception as e:
        return str(e)

# Function to handle UDP requests
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(udp_address)
        print("UDP server is listening...")
        
        while True:
            data, addr = server_socket.recvfrom(1024)
            print("Received data from:", addr)
            try:
                data = data.decode()
                n1, n2, o = data.split()
                n1 = int(n1)
                n2 = int(n2)

                # Perform the calculation and send the result back
                result = str(calculation(n1, n2, o))
            except Exception as e:
                result = f"Error: {str(e)}"
            
            server_socket.sendto(result.encode(), addr)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle calculation requests
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    n1 = data['n1']
    n2 = data['n2']
    operator = data['operator']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = f"{n1} {n2} {operator}"
        client_socket.sendto(message.encode(), udp_address)

        # Receive the response from the server
        result, _ = client_socket.recvfrom(1024)
        return jsonify({'result': result.decode()})

if __name__ == '__main__':
    # Start the UDP server in a separate thread
    threading.Thread(target=udp_server, daemon=True).start()
    
    # Start the Flask app
    app.run(host='127.0.0.1', port=5000)
