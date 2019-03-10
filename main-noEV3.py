import RPi.GPIO as GPIO
import time
import threading

from Modules import control
from Modules import sensors

from aiohttp import web
import socketio

import struct
import math
#ttyAMA0


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
m7 = 29
GPIO.setmode(GPIO.BOARD)
GPIO.setup(m7, GPIO.OUT)
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

firstSid = None

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
async def index(request):
	"""Serve the client-side application."""
	with open('index.html') as f:
		return web.Response(text=f.read(), content_type='text/html')

@sio.on('connect')
def connect(sid, environ):
    global firstSid
    print('Connected ', sid)
    if(firstSid == None):
        firstSid = sid
    print('=============================')

@sio.on('disconnect')
def disconnect(sid):
	print('disconnect ', sid)
	print('=============================')

@sio.on('order')
async def message(sid, data):
    print("Ordered To ", data['order'], " - Data Given:", data['data'])
    if(data['order'] == 'rotate'):
        globals()[data['order']](data['data'][0], data['data'][1], EncoderData)
    else:
        globals()[data['order']]()
    if(data['order'] == 'drillStop'):
        GPIO.output(m7, GPIO.LOW)
    await sio.emit('reply', room=sid)

@sio.on('givingData')
async def givingData(sid, data):
	print('Hello Data - FieldWidth: ', data['data'][0],', FieldLength: ', data['data'][1],', GapBetweenSeeds: ', data['data'][2])
	userData['FieldWidth'] = int(data['data'][0]) if data['data'][0] != None else 0
	userData['FieldLength'] = int(data['data'][1]) if data['data'][1] != None else 0
	userData['GapBetweenSeeds'] = int(data['data'][2]) if data['data'][1] != None else 0
	time.sleep(1)

@sio.on('weeds')
async def weeds(sid, data):
    print('Remove Weeds')
    RemoveWeeds()

@sio.on('waterexceeded')
async def waterexceeded(sid, data):
    print('Water Exceeded on: ')
    print(data)
    await sio.emit('waterexceeded', data)


app.router.add_static('/socket.io', 'socket.io')
app.router.add_get('/', index)

def runWebApp(app):
	try:
		web.run_app(app)
	except KeyboardInterrupt:
		return

def RemoveWeeds():
    GPIO.output(m7, GPIO.HIGH)

def mainProg():
    while True:
        if(userData["FieldWidth"] == None or userData["FieldLength"] == None or userData["GapBetweenSeeds"] == None):
            print('Awaiting')
        elif(userData["FieldWidth"] == 0 or userData["FieldLength"] == 0 or userData["GapBetweenSeeds"] == 0):
            print('Stopping')
            stop()
            userData["FieldWidth"] = None
            userData["FieldLength"] == None
            userData["GapBetweenSeeds"] == None
        else: # Starting Planting
            print('Starting Planting in 1 minute')
            fWidth  = userData["FieldWidth"]
            fLength = userData["FieldLength"]
            fGaps   = userData["GapBetweenSeeds"]
            print('Calculating')
            xTimes = math.floor(fWidth / fGaps)
            yTimes = math.floor(fLength / 60)
            print(yTimes, " ", xTimes)
            for __ in range(0, yTimes):
                if(__ != 0 and __ % 2 == 0):
                    rotate(90, 1, EncoderData)
                    Movement.goDistance(60, 1, EncoderData)
                    rotate(90, 1, EncoderData)
                if(__ % 2 != 0):
                    rotate(90, 0, EncoderData)
                    Movement.goDistance(60, 1, EncoderData)
                    rotate(90, 0, EncoderData)
                for ___ in range(0, xTimes):
                    Movement.goDistance(fGaps, 1, EncoderData)
                    time.sleep(0.3)
                    for _ in range(0, 2): drillStepDown()
                    Driller.drillClockWise()
                    for _ in range(0, 3): drillStepDown()
                    time.sleep(2)
                    drillStop()
                    for _ in range(0, 7): drillStepUp()
                    time.sleep(1)
                print("__ ", __)
            userData["FieldWidth"] = None
            userData["FieldLength"] == None
            userData["GapBetweenSeeds"] == None
        time.sleep(1)
#00:16:53:41:1E:FF
try:
    """while True:
        Movement.forward()
        time.sleep(2)
        Movement.stop()
        time.sleep(2)"""
    mainApp = threading.Thread(target=mainProg, args=[])
    mainApp.start()
    runWebApp(app)

except KeyboardInterrupt:
	GPIO.cleanup()
	exit()

