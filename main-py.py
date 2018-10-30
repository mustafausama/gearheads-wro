import RPi.GPIO as GPIO
import time
import threading

from Modules import control
from Modules import sensors

from aiohttp import web
import socketio

import serial
from Modules import EV3BT
import Modules.EV3BT
import struct
import math
#ttyAMA0

"""
import serial

print('==================', serial.__file__)
EV3 = serial.Serial('/dev/rfcomm0')
while True:
	n = EV3.inWaiting()      
	if (n != 0):         
		s = EV3.read(n)         
		for n in s:            
			print("x%02X" % ord(n))
		print

EV3.write(s)
time.sleep(1)
EV3.close()
"""

"""
-                           (Camera#)
-                               |
-                       /\     / \     /\
-           (Motor #3) |--|-----------|--| (Motor #1)
-                       \/|           |\/
-                         |           |
-                      <--|           |-->
-     (Ultrasonic #1)     |           |     (Ultrasonic #2)
-                      <--|           |-->
-                         |           |
-                       /\|           |/\
-           (Motor #4) |--|-----------|--| (Motor #2)
-                       \/     | |     \/
-                              ^ ^
-                        (Ultrasonic #3)
"""

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

m1 = 11
m2 = 12
m3 = 13
m4 = 15
encoderPin = 16
m5 = 31 # Drill
m6 = 32 # Up/Down
us1i = 19
us1o = 21
us2i = 23
us2o = 24
us3i = 26
us3o = 28

USsList = [[19, 21], [23, 24]]

Movement = control.MovementControl(m1, m2, m3, m4)
Driller  = control.DrillController(m5, m6)
Ultrasonic = sensors.Ultrasonic(USsList)
EncoderData = sensors.Encoder(encoderPin, 1, 13)

forward  = Movement.forward
backward = Movement.backward
toRight  = Movement.toRight
toLeft   = Movement.toLeft
rotate   = Movement.rotateDegree
stop     = Movement.stop
drillStepUp = Driller.stepUp
drillStepDown = Driller.stepDown
drillClockWise = Driller.drillClockWise
drillAntiClockWise = Driller.drillAntiClockWise
drillStop = Driller.drillStop

userData = {
	"FieldWidth":None,
	"FieldLength": None,
	"GapBetweenSeeds": None
}

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
	"""Serve the client-side application."""
	with open('index.html') as f:
		return web.Response(text=f.read(), content_type='text/html')

@sio.on('connect')
def connect(sid, environ):
	print('connect ', sid)

@sio.on('disconnect')
def disconnect(sid):
	print('disconnect ', sid)

@sio.on('order')
async def message(sid, data):
	print("Ordered To ", data['order'], " - Data Given:", data['data'])
	if(data['order'] == 'rotate'):
		globals()[data['order']](data['data'][0], data['data'][1], EncoderData)
	globals()[data['order']]()
	await sio.emit('reply', room=sid)

@sio.on('givingData')
async def givingData(sid, data):
	global EV3
	print('Hello Data - FieldWidth: ', data['data'][0],', FieldLength: ', data['data'][1],', GapBetweenSeeds: ', data['data'][2])
	userData['FieldWidth'] = int(data['data'][0])
	userData['FieldLength'] = int(data['data'][1])
	userData['GapBetweenSeeds'] = int(data['data'][2])
	s  = EV3BT.encodeMessage(EV3BT.MessageType.Text, 'abc', 'UserData')
	EV3.write(s)
	time.sleep(1)

	"""XTimes = math.ceil(userData['FieldLength'] / 80) + 1
	YTimes    = int(((userData['FieldWidth'] - 60) / userData['GapBetweenSeeds']))
	XT  = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, 'abc', XTimes)
	YT  = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, 'abc', YTimes)
	EV3.write(XT)
	time.sleep(1)
	EV3.write(YT)"""

app.router.add_static('/socket.io', 'socket.io')
app.router.add_get('/', index)

def runWebApp(app):
	try :
		web.run_app(app)
		print("Hello World")
	except KeyboardInterrupt:
		return
"""
#EV3 = serial.Serial('/dev/rfcomm1')
#print("Listening for EV3 Bluetooth messages, press CTRL C to quit.")

def main(ev3):
	while 1:
		n = ev3.inWaiting()
		if n != 0:
			s = EV3.read(n)
			msg = s[21:-1]
			message = msg
			print(message)
			print(message.decode())
			if(message.decode() == 'DrillClock'):
				Driller.drillClockWise()
			elif(message.decode() == 'DrillUp'):
				Driller.stepUp()
			elif(message.decode() == 'DrillDown'):
				Driller.stepDown()
			elif(message.decode() == 'DrillStop'):
				Driller.drillStop()
			elif(message.decode() == 'MoveForward'):
				Movement.goDistance(userData['GapBetweenSeeds'], 1, EncoderData)
			elif(message.decode() == 'RotateCounter'):
				Movement.rotateDegree(90, 0, EncoderData)
			elif(message.decode() == 'RotateClock'):
				Movement.rotateDegree(90, 1, EncoderData)
"""
def mainProg():
	while True:
		print("Hi World")
		time.sleep(10)
#00:16:53:41:1E:FF
try :
	webApp = threading.Thread(target=mainProg, args=[])
	webApp.start()
	runWebApp(app)
except KeyboardInterrupt:
	GPIO.cleanup()
	exit()

