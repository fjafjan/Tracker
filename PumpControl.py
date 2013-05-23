import threading
import datetime
from random import randint
import serial
from time import sleep
# CR = Carriage Return, ie enter.
class PumpController():
	def __init__(self):
		self.ser = serial.Serial(port='\\.\COM3', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
		self.CR = '\x0D'
		
	def ReverseFlow(self):
		command = 'DIR REV'+self.CR
		self.ser.write(command)

	def TestSettingRate(self):	
		command = 'RAT 2.5 UM'+self.CR
		self.ser.write(command)

	def SetRate(self,rate):
		command = "RAT "+str(rate) + " UM"+self.CR
		self.ser.write(command)

	def StartFlow(self):
		command = 'RUN'+self.CR
		self.ser.write(command)

	def StopFlow(self):
		command = 'STP'+self.CR
		self.ser.write(command)

	def IncreaseFlow(self):
		command = 'FUN LP EN'+self.CR
		self.ser.write(command)

	def ResetPump(self):
		command = 'RESET' + self.CR
		self.ser.write(command)
	
	def CloseConnection(self):
		self.ser.close()

class PumpThread(threading.Thread):
	def __init__(self, pump):
		threading.Thread.__init__(self)
		self.phrase = randint
		self.pump = pump
	def run(self):
		sleep(1)
		print "I am now about to star slowing down"
		self.slow_reverse([2.0, 1.0],10)
		# End of life? Seemingly
	def slow_reverse(self , flow_rates, pause_time):
		for rate in flow_rates[1:]:
			self.pump.StopFlow()
			print " Setting flow rate to ", rate
			self.pump.SetRate(rate)
			sleep(0.1)
			self.pump.StartFlow()
			print "Starting with slow rate"
			sleep(pause_time)
		## Do nothing for abit
		self.pump.StopFlow()
		print "stopping completely for a bit"
		sleep(pause_time)
### NOte review this
		self.pump.ReverseFlow()
		self.pump.StartFlow()
		for rate in reversed(flow_rates[:-1]):
			print "Starting with slow reversed flow"
			sleep(pause_time)
			self.pump.StopFlow()
			self.pump.SetRate(rate)
			print "Starting again with fast rate"
			sleep(0.1)
			self.pump.StartFlow()



## Unit test function
#~ 
#~ pump = PumpController()
#~ p = PumpThread(pump)
#~ p.setDaemon(False)
#~ p.start()


#~ for i in range(1,10):
	#~ sleep(1)
	#~ print "proc ", i, " has started"

#TestSettingRate()
#ResetPump
#StartFlow()
#sslow_reverse(5,1,5)
#sleep()
#IncreaseFlow()
#ResetPump()
#StopFlow()
#print ser.isOpen()
#ser.close()
#print ser.isOpen()
#ser.open()
#ReverseFlow()
#from new_era import PumpInterface
#pi = PumpInterface()
#pi.xmit('DIR RVS')
#pi = PumpInterface(port=5)
# THIS WORKS THIS IS ALL I NEED



