#~ 
from time import sleep
from Options import *
from TimeData import *

options 		= DetectorOptions()
options.extra_file = 1
options.saving_directory    = "C:\Data\Users\Alexander\Movies\Laas\April 30\position_tracking.txt"
extra_file = open(options.saving_directory,'w')
timedata		= TimeData()





for i in range(1,10*3600*20):
	SaveStepPos(options, timedata, extra_file=extra_file)
	sleep(0.1)
	print i

import threading

#~ class fulthread(threading.Thread):
	#~ def __init__(self):
		#~ threading.Thread.__init__(self)
		#~ from StepControl import *
		#~ Step5 = ctypes.WinDLL('C:/Data/dllfolder/LStep4.dll')
		#~ connect_simple = Step5['LS_ConnectSimple']
		#~ ctrl_id = ctypes.c_int(1)
		#~ com_name  = ctypes.c_char_p("COM4")
		#~ baud_rate = ctypes.c_int(9600)
		#~ show_prot = ctypes.c_int(0)
		#~ error_code= ctypes.c_int32(-1)
		#~ error_code = connect_simple(ctrl_id, com_name, baud_rate, show_prot)
		#~ print "error code is ", error_code
		#~ Disconnect()
	#~ def run(self):
		#~ from StepControl import *
		#~ print "I am ", threading.current_thread()
		#~ ConnectSimple(1, "COM4", 9600, 0)
		#~ sleep(5)
		#~ Disconnect()
#~ thread1 = fulthread()
#~ thread1.start()
#~ thread1.join()
#~ 
#~ thread2 = fulthread()
#~ thread2.start()
