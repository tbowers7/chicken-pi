import urllib2

def wifi_on():
  try:
    urllib.urlopen('http://192.168.0.1', timeout=1)
    return True
  except urllib2.URLError as err:
    return False
