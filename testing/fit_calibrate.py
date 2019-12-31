import numpy as np

data = np.genfromtxt('rotation_calibrate.csv',delimiter=',',names='time,head')

times = data['time']
heads = data['head']

inds = np.where(np.logical_and(times>=8.5, times<=12.5))
times = times[inds]
heads = heads[inds]

# Do the linear fit

p = np.polyfit(times, heads, 1)

print(p)

times = data['time']
heads = data['head']

inds = np.where(np.logical_and(times>=4.5, times<=8.4))
times = times[inds]
heads = heads[inds]

# Do the linear fit

p = np.polyfit(times, heads, 1)

print(p)

times = data['time']
heads = data['head']

inds = np.where(np.logical_and(times>=0.4, times<=4.4))
times = times[inds]
heads = heads[inds]

# Do the linear fit

p = np.polyfit(times, heads, 1)

print(p)
