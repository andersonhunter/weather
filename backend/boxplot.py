import matplotlib.pyplot as plt
import os
import zmq


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5559")

while True:

    message = socket.recv()
    print(f"Received request from the client: {message.decode()}")
    if len(message) > 0:
        if message.decode() == 'Q':  # Client asked server to quit
            break
        decoded_msg = message.decode()

        # adjust incoming strings to two decial places. 7450 --> 74.50
        temp_str_array = str(decoded_msg)
        temp_str_array = temp_str_array.split(',')
        temp_int_array = [int(i) / 100 for i in temp_str_array]

        plt.figure(figsize=(10, 6))
        plt.boxplot(temp_int_array, vert=False)
        plt.title("Five-Number Summary")
        plt.xlabel("Degrees Fahrenheit")

        image_name = 'box.png'
        static_path = os.path.abspath('../static/box.png')
        plt.savefig(static_path)

        cwd = os.getcwd()
        decoded_msg = f"File saved at location: {cwd}/{image_name}"
        socket.send_string(decoded_msg)
context.destroy()
