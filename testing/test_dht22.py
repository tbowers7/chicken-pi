import time
from tkinter import *

import adafruit_dht
import board


class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.read()
        Label(frame, text='Values 1').grid(row=0, column=0)
        Label(frame, text='Values 2').grid(row=1, column=0)
        Label(frame, text='Values 3').grid(row=2, column=0)
        
        # Create the sliders and position them in a grid layout
        # the 'command' attribute specifys a method to call when
        # a slider is moved
        scaleRed = Scale(frame, from_=0, to=100,
              orient=HORIZONTAL, command=self.updateRed)
        scaleRed.grid(row=0, column=1)
        scaleGreen = Scale(frame, from_=0, to=100,
              orient=HORIZONTAL, command=self.updateGreen)
        scaleGreen.grid(row=1, column=1)
        scaleBlue = Scale(frame, from_=0, to=100,
              orient=HORIZONTAL, command=self.updateBlue)
        scaleBlue.grid(row=2, column=1)

    # These methods called whenever a slider moves
    def updateRed(self, duty):
        print('RED!')
    def updateGreen(self, duty):
        print('GREEN!')
    def updateBlue(self, duty):
        print('BLUE!')
 


    def read(self):
        try:
            temp1 = dht1.temperature
            degf1 = temp1 * (9 / 5) + 32
            humid1 = dht1.humidity
            # Print what we got to the REPL
            print("DHT22 #1: Temp: {:.1f} *F \t Humidity: {}%".format(degf1, humid1))
        except RuntimeError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("Reading from DHT failure: ", e.args)


        time.sleep(0.1)
    
        try:
            temp2 = dht2.temperature
            degf2 = temp2 * (9 / 5) + 32
            humid2 = dht2.humidity
            # Print what we got to the REPL
            print("DHT22 #2: Temp: {:.1f} *F \t Humidity: {}%".format(degf2, humid2))
        except RuntimeError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("Reading from DHT failure: ", e.args)

        time.sleep(0.1)
        
        try:
            temp3 = dht3.temperature
            degf3 = temp3 * (9 / 5) + 32
            humid3 = dht3.humidity
            # Print what we got to the REPL
            print("DHT22 #3: Temp: {:.1f} *F \t Humidity: {}%".format(degf3, humid3))
        except RuntimeError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("Reading from DHT failure: ", e.args)


# Main Program

dht1 = adafruit_dht.DHT22(board.D19)
dht2 = adafruit_dht.DHT22(board.D20)
dht3 = adafruit_dht.DHT22(board.D21)




# Setup the display window
root = Tk()
root.wm_title('Coop Temperature')
app = App(root)
root.mainloop()
