import zmq
from statistics import median_low, median, median_high, mean, stdev, pvariance, quantiles
from math import isnan
from itertools import filterfalse


def arrayify(string):
    """Convert string into an array of floats"""
    arr = [float(item) / 100 for item in string.split(", ")]
    return arr


# def t_test(mean, sd, dataset) -> float:
#     """Perform a t-test on the retrieved dataset"""
#     # Subtract mean datapoint from each individual datapoint
#     mean_from_indv = 0
#     for datapoint in dataset:
#         mean_from_indv += (datapoint - mean) ** 2
#     t = int(round((mean_from_indv / sd) / (len(dataset) ** 0.5), 2))
#     print(f'T value: {t}')
#     return t


def generate_statistics(dataset: list) -> list:
    """Generate the summary statistics for the retrieved dataset"""
    minimum = int(round(min(dataset), 2) * 100)
    maximum = int(round(max(dataset), 4) * 100)
    iqr = [round(q, 1) for q in quantiles(dataset, n=4)]
    first_quartile = int(round(iqr[0], 2) * 100)
    med = int(round(median(dataset), 2) * 100)
    third_quartile = int(round(iqr[2], 2) * 100)
    average = int(round(mean(dataset), 2) * 100)
    sd = int(round(stdev(dataset), 2) * 100)
    variance = int(round(pvariance(dataset), 2) * 100)

    summary = [minimum,  maximum, first_quartile, med, third_quartile, average, sd, variance]
    return summary


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

while True:
    message = socket.recv()
    print(f"Rec'd req from client: {message.decode()}")
    if len(message) > 0:
        response_body = message.decode()
        array_dataset = arrayify(response_body)
        summary = generate_statistics(array_dataset)
        print(f'Sending summary statistics to client: {summary} of type {type(summary)}')
        socket.send_string(str(summary))
