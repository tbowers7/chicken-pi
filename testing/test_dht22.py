import time

import adafruit_dht
from board import D19

dht = adafruit_dht.DHT22(D19)

while True:
    try:
        temperature = dht.temperature
        degf = temperature * (9 / 5) + 32
        humidity = dht.humidity
        # Print what we got to the REPL
        print("Temp: {:.1f} *F \t Humidity: {}%".format(degf, humidity))
    except RuntimeError as e:
        # Reading doesn't always work! Just print error and we'll try again
        print("Reading from DHT failure: ", e.args)

    time.sleep(1)
