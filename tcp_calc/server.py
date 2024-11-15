from flask import Flask, request, jsonify, render_template
import socket
import threading

app = Flask(__name__)

# TCP server settings
tcp_address = ('127.0.0.1', 8000)

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

# Function to handle TCP requests
def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(tcp_address)
        server_socket.listen()
        print("TCP server is listening...")
        
        while True:
            connection_socket, addr = server_socket.accept()
            with connection_socket:
                print("Connected by", addr)
                data = connection_socket.recv(1024)
                if not data:
                    break
                
                try:
                    data = data.decode()
                    n1, n2, o = data.split()
                    n1 = int(n1)
                    n2 = int(n2)

                    # Perform the calculation and send the result back
                    result = str(calculation(n1, n2, o))
                except Exception as e:
                    result = f"Error: {str(e)}"
                
                connection_socket.sendall(result.encode())

# Route to render the HTML page (frontend)
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

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(tcp_address)
        message = f"{n1} {n2} {operator}"
        client_socket.sendall(message.encode())

        # Receive the response from the server
        result = client_socket.recv(1024).decode()
        return jsonify({'result': result})

if __name__ == '__main__':
    # Start the TCP server in a separate thread
    threading.Thread(target=tcp_server, daemon=True).start()
    
    # Start the Flask app
    app.run(host='127.0.0.1', port=5002)
