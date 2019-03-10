import RPi.GPIO as GPIO
import time
import threading
import math
class MovementControl(threading.Thread):
	# Pulses that control the motors' rotation direction as servos
	__clockwisePulse = 6
	__antiClockwisePulse = 9
	def motorHa(self):
		self.motor1.ChangeDutyCycle(self.__clockwisePulse)

	# Initialize the motors and create class attribute for every motor
	def __init__(self, motorRightFront, motorRightBack, motorLeftFront, motorLeftBack):
		super(MovementControl, self).__init__()
		self._stop_event = threading.Event()
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(motorRightFront, GPIO.OUT)
		GPIO.setup(motorRightBack, GPIO.OUT)
		GPIO.setup(motorLeftFront, GPIO.OUT)
		GPIO.setup(motorLeftBack, GPIO.OUT)

		self.motor1 = GPIO.PWM(motorRightFront, 50)
		self.motor2 = GPIO.PWM(motorRightBack, 50)
		self.motor3 = GPIO.PWM(motorLeftFront, 50)
		self.motor4 = GPIO.PWM(motorLeftBack, 50)

		self.motor1.start(0)
		self.motor2.start(0)
		self.motor3.start(0)
		self.motor4.start(0)
		
	def __ThreadStop(self):
 		self._stop_event.set()

	# Public Control
	def forward(self):
		process = threading.Thread(target=self.__forward)
		process.start()
	def __forward(self):
		print('Robot to Front')
		self.__ThreadStop()
		for diff in range(self.__antiClockwisePulse - 7, -1, -1):
			self.motor1.ChangeDutyCycle(self.__clockwisePulse+diff)
			self.motor2.ChangeDutyCycle(self.__clockwisePulse+diff)
			self.motor3.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			self.motor4.ChangeDutyCycle(self.__antiClockwisePulse-diff)
		
	def backward(self):
		process = threading.Thread(target=self.__backward)
		process.start()
	def __backward(self):
		self.__ThreadStop()
		print('Robot to Back')
		for diff in range(self.__antiClockwisePulse - 7, -1, -1):
			self.motor1.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			self.motor2.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			self.motor3.ChangeDutyCycle(self.__clockwisePulse+diff)
			self.motor4.ChangeDutyCycle(self.__clockwisePulse+diff)
			time.sleep(0.2)

	def toRight(self):
		process = threading.Thread(target=self.__toRight)
		process.start()
	def __toRight(self):
		self.__ThreadStop()
		print('Robot to Right')
		for diff in range(self.__antiClockwisePulse - 7, -1, -1):
			self.motor1.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			self.motor2.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			self.motor3.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			self.motor4.ChangeDutyCycle(self.__antiClockwisePulse-diff)
			time.sleep(0.5)

	def toLeft(self):
		process = threading.Thread(target=self.__toLeft)
		process.start()
	def __toLeft(self):
		self.__ThreadStop()
		print('Robot to Left')
		for diff in range(self.__antiClockwisePulse - 7, -1, -1):
			print('Diff: ', diff)
			self.motor1.ChangeDutyCycle(self.__clockwisePulse+diff)
			self.motor2.ChangeDutyCycle(self.__clockwisePulse+diff)
			self.motor3.ChangeDutyCycle(self.__clockwisePulse+diff)
			self.motor4.ChangeDutyCycle(self.__clockwisePulse+diff)
			time.sleep(3)

	def stop(self):
		self.__ThreadStop()
		self.motor1.ChangeDutyCycle(0)
		self.motor2.ChangeDutyCycle(0)
		self.motor3.ChangeDutyCycle(0)
		self.motor4.ChangeDutyCycle(0)

	def goDistance(self, distance, direction, encoderData):
		initialDistance = encoderData.distanceTravelled()
		if direction == 1:
			self.forward()
			while encoderData.distanceTravelled() - initialDistance < distance:
				True
			self.stop()
		elif direction == 0:
			self.backward()
			while encoderData.distanceTravelled() - initialDistance < distance:
				True
			self.stop()
	def rotateDegree(self, degrees, direction, encoderData):
		process = threading.Thread(target=self.__rotateDegree, args=[degrees, direction, encoderData])
		process.start()
	def __rotateDegree(self, degrees, direction, encoderData):
		self.__ThreadStop()
		distanceToTravel = 18.56 * math.pi / 2
		initialDistance = encoderData.distanceTravelled()
		if direction == 1:
			print('Direction ', 1)
			self.toRight()
			while encoderData.distanceTravelled() - initialDistance < distanceToTravel:
				True
			self.stop()
		elif direction == 0:
			print('Direction ', 0)
			self.toLeft()
			while encoderData.distanceTravelled() - initialDistance < distanceToTravel:
				True
			self.stop()

class DrillController:
	__clockwisePulse = 6
	__antiClockwisePulse = 8

	def __init__(self, drill, elevator):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(drill, GPIO.OUT)
		GPIO.setup(elevator, GPIO.OUT)

		self.__drill = GPIO.PWM(drill, 50)
		self.__elevator = GPIO.PWM(elevator, 50)

		self.__drill.start(0)
		self.__elevator.start(0)

	def drillClockWise(self):
		for diff in range(self.__antiClockwisePulse - 7, -1, -1):
			self.__drill.ChangeDutyCycle(self.__clockwisePulse+diff)
			time.sleep(0.2)

	def drillAntiClockWise(self):
		for diff in range(self.__antiClockwisePulse - 7, -1, -1):
			self.__drill.ChangeDutyCycle(self.__antiClockwisePulse+diff)
			time.sleep(0.2)

	def drillStop(self):
		self.__drill.ChangeDutyCycle(0)

	def stepUp(self):
		self.__elevator.ChangeDutyCycle(self.__antiClockwisePulse)
		time.sleep(0.2)
		self.__elevator.ChangeDutyCycle(0)

	def stepDown(self):
		self.__elevator.ChangeDutyCycle(self.__clockwisePulse)
		time.sleep(0.05)
		self.__elevator.ChangeDutyCycle(0)

