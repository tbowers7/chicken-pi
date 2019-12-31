# Import needed modules
import numpy as np
import time
import Adafruit_LSM303
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from ellipses import LSqEllipse
from matplotlib.patches import Ellipse
from eugenebot import eugenebot
import csv

current_milli_time = lambda: int(round(time.time() * 1000))

# Define Callibration Offsets
MX_OFF = +41
MY_OFF = -191
MZ_OFF = 0

robot = eugenebot()


# Create a LSM303 instance
lsm303 = Adafruit_LSM303.LSM303(mx_off=MX_OFF, my_off=MY_OFF)
lsm303.set_mag_gain(Adafruit_LSM303.LSM303_MAGGAIN_1_3)

robot.right(50)


# Set up values
acc_list = []
mag_list = []
ax = []
ay = []
az = []
mx = []
my = []
mz = []
head = []
eltm = []

npts = int(1200/5)

start_time = current_milli_time()

print("Start!")
for i in range(0,npts):

    accel, mag = lsm303.read()
    roll, pitch, heading = lsm303.get_orientation(accel, mag)
    
    # Unpack the raw values
    acc_x, acc_y, acc_z = accel
    mag_x, mag_y, mag_z = mag

    # Compute length of vectors
    m_acc = lsm303.hypot3(acc_x, acc_y, acc_z)
    m_mag = lsm303.hypot3(mag_x, mag_y, mag_z)

    # Add this measurement to the appropriate lists
    acc_list.append(m_acc)
    mag_list.append(m_mag)

    ax.append(acc_x)
    ay.append(acc_y)
    az.append(acc_z)
    mx.append(mag_x)
    my.append(mag_y)
    mz.append(mag_z)
    head.append(heading)
    eltm.append((current_milli_time() - start_time)/1000.)

    if ((i+1) % 100) == 0:
        percent = (i+1)/npts * 100
        degrees = int(percent) / 100 * 360
        print("{0:.0f}% -- {1:.0f} deg".format(percent, degrees))
    
    time.sleep(0.05)



robot.stop()
robot.gpio_release()

    
# Compute the means
mu_ax = np.mean(ax)
mu_ay = np.mean(ay)
mu_az = np.mean(az)
mu_mx = np.mean(mx)
mu_my = np.mean(my)
mu_mz = np.mean(mz)

print(mu_ax, mu_ay, mu_az)
print(mu_mx, mu_my, mu_mz)



# Make the Figure    
fig = plt.figure(figsize=(9,7))

ax1 = fig.add_subplot(331)
ax1.set_xlabel('ax')
ax1.set_ylabel('ay')
ax1.plot(ax, ay, color='red')
ax1.plot(ax, np.repeat(mu_ay,npts), '--', color='purple', alpha=0.4)
ax1.plot(np.repeat(mu_ax,npts), ay, '--', color='purple', alpha=0.4)
ax1.axis('equal')

ax2 = fig.add_subplot(332)
ax2.set_xlabel('ax')
ax2.set_ylabel('az')
ax2.plot(ax, az, color='red')
ax2.plot(ax, np.repeat(mu_az,npts), '--', color='purple', alpha=0.4)
ax2.plot(np.repeat(mu_ax,npts), az, '--', color='purple', alpha=0.4)
ax2.axis('equal')

ax3 = fig.add_subplot(333)
ax3.set_xlabel('ay')
ax3.set_ylabel('az')
ax3.plot(ay, az, color='red')
ax3.plot(ay, np.repeat(mu_az,npts), '--', color='purple', alpha=0.4)
ax3.plot(np.repeat(mu_ay,npts), az, '--', color='purple', alpha=0.4)
ax3.axis('equal')

ax4 = fig.add_subplot(334)
ax4.set_xlabel('mx')
ax4.set_ylabel('my')
ax4.plot(mx, my, color='red')
ax4.axis('equal')

ax5 = fig.add_subplot(335)
ax5.set_xlabel('mx')
ax5.set_ylabel('mz')
ax5.plot(mx, mz, color='red')
ax5.axis('equal')

ax6 = fig.add_subplot(336)
ax6.set_xlabel('my')
ax6.set_ylabel('mz')
ax6.plot(my, mz, color='red')
ax6.axis('equal')

ax7 = fig.add_subplot(313)
ax7.set_xlabel('Time [s]')
ax7.set_ylabel('Heading [deg]')
ax7.plot(eltm, head, color='green')

# Now, try to fit an ellipse to the mx-my data
lsqe = LSqEllipse()

mxmy = np.vstack((mx,my))
lsqe.fit(mxmy)
center, width, height, phi = lsqe.parameters()
ellipse = Ellipse(xy=center, width=2*width, height=2*height,
                  angle=np.rad2deg(phi),edgecolor='b', fc='None',
                  lw=2, label='Fit', zorder = 2)
ax4.add_patch(ellipse)
ax4.plot(mx, np.repeat(center[1],npts), '--', color='purple', alpha=0.4)
ax4.plot(np.repeat(center[0],npts), my, '--', color='purple', alpha=0.4)

print("Ellipse center=({0:.1f},{1:.1f}), width={2:.1f}, height={3:.1f}, phi={4:.1f}".format(center[0], center[1], width, height, np.rad2deg(phi)))


# Next, do for the mx-mz data
mxmz = np.vstack((mx,mz))
lsqe.fit(mxmz)
center, width, height, phi = lsqe.parameters()
ellipse = Ellipse(xy=center, width=2*width, height=2*height,
                  angle=np.rad2deg(phi),edgecolor='b', fc='None',
                  lw=2, label='Fit', zorder = 2)
ax5.add_patch(ellipse)
ax5.plot(mx, np.repeat(center[1],npts), '--', color='purple', alpha=0.4)
ax5.plot(np.repeat(center[0],npts), mz, '--', color='purple', alpha=0.4)

print("Ellipse center=({0:.1f},{1:.1f}), width={2:.1f}, height={3:.1f}, phi={4:.1f}".format(center[0], center[1], width, height, np.rad2deg(phi)))


# Next, do for the my-mz data
mymz = np.vstack((my,mz))
lsqe.fit(mymz)
center, width, height, phi = lsqe.parameters()
ellipse = Ellipse(xy=center, width=2*width, height=2*height,
                  angle=np.rad2deg(phi),edgecolor='b', fc='None',
                  lw=2, label='Fit', zorder = 2)
ax6.add_patch(ellipse)
ax6.plot(my, np.repeat(center[1],npts), '--', color='purple', alpha=0.4)
ax6.plot(np.repeat(center[0],npts), mz, '--', color='purple', alpha=0.4)

print("Ellipse center=({0:.1f},{1:.1f}), width={2:.1f}, height={3:.1f}, phi={4:.1f}".format(center[0], center[1], width, height, np.rad2deg(phi)))


fig.savefig('./lsm303_calibrate.png', bbox_inches='tight')

# Write out calibration data to CSV file
with open('rotation_calibrate.csv', 'w', newline='') as csvfile:
    filewrite = csv.writer(csvfile, delimiter=',')
    for t,h in zip(eltm, head):
        filewrite.writerow([t, h])
        
