import flask
from flask import Flask, render_template, request
import os
import zmq
import subprocess

# Configuration

app = Flask(__name__)


# Routes

@app.route('/')
def root():
    return render_template("home.html")


@app.route('/analyze-data')
def analyzedata():
    return render_template("analyze-data.html")


@app.route('/contact-faq')
def contactfaq():
    return render_template("contact-faq.html")


@app.route('/delete-account')
def deleteaccount():
    return render_template("delete-account.html")


@app.route('/login-signup')
def loginsignup():
    return render_template("login-signup.html")


@app.route('/results')
def results():
    return render_template("results.html")


@app.route('/get-data', methods=['GET', 'POST'])
def getdata():
    """
    Receive POSTed search criteria from analyze-data.html, then pipe over to get-data.py.
    Then, pipe data over to analyze-data.py.
    Finally, POST analyzed data to results.html.
    """
    if request.method == 'POST':
        startdate = request.form.get('startdate')
        enddate = request.form.get('enddate')
        location = request.form.get('location')
        indices = request.form.get('indices')

        # Pipe data over to get-data
        context = zmq.Context()
        print("Client attempting to connect to server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")
        print(f'Sending request:\n'
              f'Start date = {startdate}\n'
              f'End date = {enddate}\n'
              f'Location = {location}\n'
              f'Index = {indices}')
        socket.send_string(f"{startdate}, {enddate}, {location}, {indices}")

        # Receive the fetched data
        message = socket.recv()
        print(f'get-data.py sent back: {message.decode()}')

        # Pipe the fetched data over to generate a graph
        graph_data = message.decode()
        subprocess.Popen(['python', './backend/ms_server.py'])
        subprocess.run(['python', './backend/ms_client.py', graph_data])

        # Pipe the fetched data over to analyze-data.py
        analyze_socket = context.socket(zmq.REQ)
        analyze_socket.connect("tcp://localhost:5556")
        print("Sending request to analyze-data.py")
        analyze_socket.send_string(message.decode())

        # Receive the analyzed data
        message = analyze_socket.recv()
        print(f'analyze-data.py sent back: {message.decode()} of type {type(message.decode())}')

        # Send the analyzed data to the data analysis page
        print(f'Sending to results: {message.decode()}')
        return render_template("results.html", data=message.decode())


# Listener

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    #                                 ^^^^
    #              You can replace this number with any valid port

    app.run(port=port)
