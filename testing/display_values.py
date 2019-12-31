# Use Tkinter to display values from the LSM303  accelerometer & magnetometer
#
from tkinter import *
import time
root = Tk()

# Import the LSM303 module.
import Adafruit_LSM303


# Define Callibration Offsets
MX_OFF = +36
MY_OFF = -188
MZ_OFF = 0
MAG_DECL = +10.5


# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303(mx_off=MX_OFF, my_off=MY_OFF, mag_decl=MAG_DECL)
lsm303.set_mag_gain(Adafruit_LSM303.LSM303_MAGGAIN_1_3)

# Set up display string
val1 = ''
disp = Label(root, font=('courier', 25, 'bold'), bg='black', fg='yellow')
disp.pack(fill=BOTH, expand=1)

# Function for updating string for display
def update():
    global val1

    # Get the raw values from the LSM303 & compute orientation
    accel, mag = lsm303.read()
    roll, pitch, heading = lsm303.get_orientation(accel, mag)

    # Unpack the raw values
    accel_x, accel_y, accel_z = accel
    mag_x,   mag_y,   mag_z   = mag

    # Compute length of vectors
    m_accel = lsm303.hypot3(accel_x, accel_y, accel_z)
    m_mag   = lsm303.hypot3(mag_x,   mag_y,   mag_z)

    # Create the output string
    val2 = "Accel: {0:5d}, {1:5d}, {2:5d}\nMag:   {3:5d}, {4:5d}, {5:5d}\n|Accel| = {6:5.0f}\n |Mag|  = {7:5.0f}\nRoll:    {8:4.0f}\nPitch:   {9:4.0f}\nHeading: {10:4.0f}".format(
        accel_x, accel_y, accel_z, mag_x, mag_y, mag_z, m_accel, m_mag, roll, pitch, heading)
    if val2 != val1:
        val1 = val2
        disp.config(text=val2)

    # Calls itself every 1000 ms to update the display
    disp.after(1000, update)

update()
root.winfo_toplevel().title("LSM303 on Pi -- Orientation Sensor")
root.mainloop()

