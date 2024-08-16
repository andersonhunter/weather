import zmq
import sys

string = sys.argv[1]
context = zmq.Context()
print("Client attempting to connect to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print(f"Sending a request...")
socket.send_string(string)
message = socket.recv()
print(f"Server sent back: {message.decode()}")
socket.send_string("Q")


