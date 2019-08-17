import socket
from time import sleep_ms

html = b"""
<!DOCTYPE html><html><body>
  <h1>hello world</h1>
  <button onclick="navigate('on')">on</button>
  <button onclick="navigate('off')">off</button>
</body>
<script type="text/javascript">
function toggle(value) {
  console.log('posting', value)
  window.fetch('/', {
    method: 'POST',
    body: value
  })
  .then(console.log, console.error)
}
function navigate(value) {
  console.log('navigating', value)
  window.location.replace('/' + value)
}
</script></html>
"""

# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()

# - - - NETWORKING - - - 
import network
sta_if = network.WLAN(network.STA_IF)

def connectWifi():
  sta_if.active(True)

  # PSID and password for wifi
  sta_if.connect('', '')
  return sta_if
def disconnectWifi():
  sta_if.active(False)

if not sta_if.isconnected():
  print('connecting to network...')
  connectWifi()
  while not sta_if.isconnected():
    pass
print('network config:', sta_if.ifconfig())

from machine import Pin
from time import sleep

pin = Pin(0, Pin.OPEN_DRAIN)
pin(1)

s = socket.socket()
ai = socket.getaddrinfo("0.0.0.0", 8080)
print("Bind address info:", ai)
addr = ai[0][-1]
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(addr)
s.listen(5)
print("Listening, connect your browser to http://{}:8080/".format(addr))

class Headers(object):
  def __init__(self, headers):
    self.__dict__.update(headers)

  def __getitem__(self, name):
    return getattr(self, name)

  def get(self, name, default=None):
    return getattr(self, name, default)

class Request(object):
  def __init__(self, sock):
    header_off = -1
    data = ''
    while header_off == -1:
      data += sock.recv(2048).decode('utf-8')
      header_off = data.find('\r\n\r\n')
    header_string = data[:header_off]
    self.content = data[header_off+4:]

    print('data', data)

    # lines = []
    # while len(header_string) > 0:
    #   match = self.header_re.search(header_string)
    #   group = match.group(0)
    #   print('mathc', group)
    #   lines.append(group)
    #   header_string = header_string[len(group) + 2:]
    lines = header_string.split('\r\n')

    first = lines.pop(0)
    self.method, path, protocol = first.split(' ')
    self.headers = Headers(
      (header.split(': ')[0].lower().replace('-', '_'), header.split(': ')[1]) for header in lines
    )
    self.path = path

    if self.method in ['POST', 'PUT']:
      content_length = int(self.headers.get('content_length', 0))
      while len(self.content) < content_length:
        self.content += sock.recv(4096).decode('utf-8')
      
      if self.content == 'on':
        turnOn()
      elif self.content == 'off':
        turnOff()

def turnOn():
  print('turning on')
  pin(0)
  sleep_ms(1450)
  pin(1)

def turnOff():
  print('turning off')
  pin(0)
  sleep_ms(3500)
  pin(1)

while True:
  socket, addr = s.accept()

  print('client connected from', addr)

  req = Request(socket) 
  if req.path == '/on':
    turnOn()
  elif req.path == '/off':
    turnOff()

  if req.method == 'POST':
    print('this was a post')
  print('req', req.path)
  print('content', req.content)

  socket.send(b'HTTP/1.1 200 OK\n\n' + html)
  socket.close()

