import urllib3
import socket

def wifi_on(host='192.168.0.1'):
  try:
    http = urllib3.PoolManager()
    http.request('GET', host, timeout=3, retries=False)
    return True
  except urllib3.exceptions.NewConnectionError:
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
  except socket.error as ex:
    return False


print(wifi_on())
print(wifi_on2())
