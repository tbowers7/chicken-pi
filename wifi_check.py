import urllib2
import socket

def wifi_on():
  try:
    urllib.urlopen('http://192.168.0.1', timeout=1)
    return True
  except urllib2.URLError as err:
    return False

  
def wifi_on2(host='8.8.8.8', port=53, timeout=3):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
     socket.setdefaulttimeout(timeout)
     socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
     return True
   except socekt.error as ex:
     print(ex)
     return False

wifi_on()
wifi_on2()
