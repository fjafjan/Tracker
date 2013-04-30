from StepControl import *
from time import sleep
from Options import *
from TimeData import *

options 		= DetectorOptions()
options.extra_file = 1
options.saving_directory    = "C:\Data\Users\Alexander\Movies\Laas\April 30\position_tracking.txt"
extra_file = open(options.saving_directory,'w')
timedata		= TimeData()
ConnectSimple(1, "COM4", 9600, 0)

for i in range(1,10*3600*20):
	SaveStepPos(options, timedata, extra_file=extra_file)
	sleep(0.01)
	print i

