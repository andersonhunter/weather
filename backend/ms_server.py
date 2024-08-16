import time
import zmq
import random
import os

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:

    message = socket.recv()
    print(f"Received request from the client: {message.decode()}")
    if len(message) > 0:
        if message.decode() == 'Q': # Client asked server to quit
            break
    decoded_msg = message.decode()

    # adjust incoming strings to two decial places. 7450 --> 74.50
    temp_str_array = str(decoded_msg)
    temp_str_array = temp_str_array.split(',')
    temp_int_array = [int(i)/100 for i in temp_str_array]


    #### GRAPHING ####
    import matplotlib.pyplot as plt
    import numpy as np

    # make data:
    y = temp_int_array
    x = np.array([i for i in range(len(y))])

    plt.figure(figsize=(10, 6))
    plt.plot(x, y)

    plt.title('Temperatures each day (F)')
    plt.xlabel('Day')
    plt.ylabel('Temperature (F)')
    plt.xticks(ticks=np.arange(len(y)))

    image_name = 'graph.png'
    plt.savefig(image_name)

    cwd = os.getcwd()
    decoded_msg = f"File saved at location: {cwd}/{image_name}"
    socket.send_string(decoded_msg)
context.destroy()

