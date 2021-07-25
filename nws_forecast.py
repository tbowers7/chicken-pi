from noaa_sdk import noaa
from datetime import datetime

n = noaa.NOAA()

# Coordinates of the chicken coop
forecast = n.points_forecast(35.2561,-111.5340,hourly=False)

nperiods = len(forecast['properties']['periods'])

highTemp = []
highDate = []
lowTemp = []
lowDate = []

for x in range(0,nperiods):

    startBlock = datetime.strptime(
        forecast['properties']['periods'][x]['startTime'],"%Y-%m-%dT%H:%M:%S%z")
    endBlock = datetime.strptime(
        forecast['properties']['periods'][x]['endTime'],"%Y-%m-%dT%H:%M:%S%z")
    midpoint = (startBlock + (endBlock - startBlock)/2)
    
    if forecast['properties']['periods'][x]['isDaytime']:
        highTemp.append(forecast['properties']['periods'][x]['temperature'])
        highDate.append(midpoint)
    else:
        lowTemp.append(forecast['properties']['periods'][x]['temperature'])
        lowDate.append(midpoint)
        
    print(forecast['properties']['periods'][x]['number'])
    print(forecast['properties']['periods'][x]['isDaytime'])
    # print(forecast['properties']['periods'][x]['startTime'])
    # print(forecast['properties']['periods'][x]['endTime'])
    print(midpoint)
    print(forecast['properties']['periods'][x]['name'])
    print(forecast['properties']['periods'][x]['temperature'])
    print(forecast['properties']['periods'][x]['shortForecast'])
    print('-'*20)


print(forecast['properties']['periods'][0].keys())

print(highTemp)
print(highDate)
print(lowTemp)
print(lowDate)
