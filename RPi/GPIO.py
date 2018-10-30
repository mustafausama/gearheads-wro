BOARD = 1
OUT = 1
IN = 1
HGIH = 1
LOW = 0

def setmode(a):
   print a
def setup(a, b):
   print a
def output(a, b):
   print a
def cleanup():
   print 'a'
def setmode(a):
   print a
def setwarnings(flag):
   print 'False'
class PWM:
   def __init__(self, pin, freq):
      print pin, freq
   def start(self, freq):
      print freq