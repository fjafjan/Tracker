from StepControl import *

def stopnow():
	ConnectSimple(1, "COM5", 9600, 0)
	StopAxes()

stopnow()
