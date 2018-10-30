import RPi.GPIO as GPIO
import time
import threading

class Ultrasonic:

	def __init__(self, ultrasonics):
		GPIO.setmode(GPIO.BOARD)
		""" [
				[10, 11],
				[12, 13],
				[14, 15]
			] """
		self.usTrig = []
		self.usEcho = []
		for i in range(len(ultrasonics)):
			print('I is: ', i)
			self.usTrig.append(ultrasonics[i][0])
			self.usEcho.append(ultrasonics[i][1])
			GPIO.setup(ultrasonics[i][0], GPIO.OUT)
			GPIO.setup(ultrasonics[i][1], GPIO.IN)

	def usData(self, usID):

		GPIO.output(self.usTrig[usID], True)
		time.sleep(0.00001)
		GPIO.output(self.usTrig[usID], False)

		endTime = 0
		startTime = time.time()  #  add this new time stamp

		while GPIO.input(self.usEcho[usID]) == 0:
			startTime = time.time()
		while GPIO.input(self.usEcho[usID]) == 1:
			endTime = time.time()

		timeElapsed = endTime - startTime
		distance = timeElapsed * 17150
		return distance
	
	def isWall(self, usID):
		return True if self.usData(usID) < 10 or self.usData(usID) > 500 else False

class Encoder:

	def __init__(self, encoderPin, countOn, diameter):
		GPIO.setmode(GPIO.BOARD)
		self.__distanceTravelled = 0
		self.__encoderPin = encoderPin
		self.__circumference = diameter * (22/7.0)
		GPIO.setup(self.__encoderPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		process = threading.Thread(target=self.__encoderCounter, args=[countOn])
		process.start()

	def distanceTravelled(self):
		return self.__distanceTravelled
	
	def __encoderCounter(self, countOn):
		prev_input = total = 0
		while True:
			input = GPIO.input(self.__encoderPin)
			if ((not prev_input) and input):
				total = total + 1
			prev_input = input
			if total == countOn:
				self.__distanceTravelled += (countOn/90.0) * self.__circumference
				total = 0
