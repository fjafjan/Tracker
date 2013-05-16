import ctypes
from time import sleep, clock, localtime
from time import time as time_now
from numpy import array
from math import sqrt, copysign, floor
import sys, os

from utilities import to_str, get_filename
## Load the DLL HERE

## Step4 = ctypes.WinDLL('C:/Documents and Settings/Fjafjan/My Documents/Downloads/LStepAPI_1_2_0_46/LStep4.dll')

Step4 = ctypes.WinDLL('C:/Data/dllfolder/LStep4.dll')
filename = get_filename("MetaData/position_tracking.txt")
outfile = open(filename, 'w')


##########		Here are some functions from the L_STEP API implemented as Python functions		##########

def ConnectSimple(ControllerID, ComName, Baudrate, ShowProtocoll, print_error=False):
	connect_simple = Step4['LS_ConnectSimple']
	ctrl_id = ctypes.c_int(ControllerID)
	com_name  = ctypes.c_char_p(ComName)
	baud_rate = ctypes.c_int(Baudrate)
	show_prot = ctypes.c_int(ShowProtocoll)
	error_code= ctypes.c_int32(-1)
	error_code = connect_simple(ctrl_id, com_name, baud_rate, show_prot)
	if print_error or error_code != 0:
		print "we get the error code ", error_code

def SetVelocity(x_vel, y_vel, z_vel, a_vel, max_vel=2.0, print_error=False):
	SetVel = Step4['LS_SetVel']
	x_vel_c = ctypes.c_double(min(x_vel,max_vel))
	y_vel_c = ctypes.c_double(min(y_vel,max_vel))
	z_vel_c = ctypes.c_double(min(z_vel,max_vel))
	a_vel_c = ctypes.c_double(min(a_vel,max_vel))
	error_code= ctypes.c_int32(-1)	
	error_code = SetVel(x_vel_c,y_vel_c,z_vel_c,a_vel_c)
	if print_error or error_code != 0:
		print "we tries setting speed to ", x_vel_c, y_vel_c, " and we got error code ", error_code

def SetPosition(X, Y, Z, A, print_error=False):
	set_position = Step4['LS_SetPos']
	x_pos = ctypes.c_double(X)
	y_pos = ctypes.c_double(Y)
	z_pos = ctypes.c_double(Z)
	a_pos = ctypes.c_double(A)
	error_code = ctypes.c_int32(-1)
	error_code = set_position(x_pos,y_pos, z_pos, a_pos)
	if print_error or error_code != 0:
		print "Our error code for moving was ", error_code

def GetPosition(print_error=False):
	GetPos = Step4['LS_GetPos']
	x_pos_c = ctypes.c_double(2)
	y_pos_c = ctypes.c_double(2)
	z_pos_c = ctypes.c_double(2)
	a_pos_c = ctypes.c_double(2)	
	error_code= ctypes.c_int32(-1)
	error_code = GetPos(ctypes.byref(x_pos_c),ctypes.byref(y_pos_c),ctypes.byref(z_pos_c),ctypes.byref(a_pos_c))
	return array([x_pos_c.value, y_pos_c.value, z_pos_c.value, a_pos_c.value])


def MoveToAbsolutePosition(X, Y, Z, A, wait, print_error=False):
	move_to_abs = Step4['LS_MoveAbs']
	x_pos = ctypes.c_double(X)
	y_pos = ctypes.c_double(Y)
	z_pos = ctypes.c_double(Z)
	a_pos = ctypes.c_double(A)
	wait_bool  = ctypes.c_int(wait)
	error_code = ctypes.c_int32(-1)
	error_code = move_to_abs(x_pos,y_pos, z_pos, a_pos, wait_bool)
	if print_error or error_code != 0:
		print "Our error code for moving was ", error_code

def Disconnect(print_error=False):
	disconnect = Step4['LS_Disconnect']
	error_code = ctypes.c_int32(-1)
	error_code = disconnect()
	if error_code != 0:
		print "Our error code for disconnecting was ", error_code
	

def SetJoystickOn(pos_count=True, encoder=True, print_error=False):
	pos_count_c = ctypes.c_int(pos_count)
	encoder_c   = ctypes.c_int(encoder)
	set_joystick_on = Step4['LS_SetJoystickOn']
	error_code = ctypes.c_int32(-1)
	error_code = set_joystick_on(pos_count_c, encoder_c)
	if print_error or error_code != 0:
		print "setting joystick on gave us error code ", error_code

def SetJoystickOff(print_error=False):
	set_joystick_off = Step4['LS_SetJoystickOff']
	error_code = ctypes.c_int32(-1)
	error_code = set_joystick_off()
	if print_error or error_code != 0:
		print "setting joystick off gave us error code ", error_code

def SetSpeed(x_speed, y_speed, z_speed, a_speed, max_speed=5.0, print_error=False):
	set_speed = Step4['LS_SetDigJoySpeed']
	x_speed_c = ctypes.c_double(copysign(min(abs(x_speed),max_speed), x_speed))
	y_speed_c = ctypes.c_double(copysign(min(abs(y_speed),max_speed), y_speed))
	z_speed_c = ctypes.c_double(copysign(min(abs(z_speed),max_speed), z_speed))
	a_speed_c = ctypes.c_double(copysign(min(abs(a_speed),max_speed), a_speed))
	if abs(x_speed) > max_speed:
		print "WHAT THE FUCK!!!! x_speed is ", x_speed
		StopAxes()
	if abs(y_speed) > max_speed:
		print "WHAT THE FUCK!!!! y_speed is ", y_speed
		StopAxes()
	error_code = ctypes.c_int32(-1)
	error_code = set_speed(x_speed_c, y_speed_c, z_speed_c, a_speed_c)
	if print_error or error_code != 0:
		print "setting speed to " , [x_speed, y_speed], "gave us error code ", error_code


def GetSpeed(print_error=False):
	get_speed = Step4['LS_GetDigJoySpeed']
	x_speed = ctypes.c_double(2)
	y_speed = ctypes.c_double(2)
	z_speed = ctypes.c_double(2)
	a_speed = ctypes.c_double(2)	
	error_code = ctypes.c_int32(-1)
	error_code = get_speed(ctypes.byref(x_speed), ctypes.byref(y_speed), ctypes.byref(z_speed), ctypes.byref(a_speed))
	if print_error or error_code != 0:
		print "getting speed gave us error core ", error_code
	return array([x_speed.value, y_speed.value, z_speed.value, a_speed.value])

def StopAxes(print_error=False):
	stop_axis = Step4['LS_StopAxes']
	error_code = ctypes.c_int32(-1)
	error_code = stop_axis()
	if print_error or error_code != 0:
		print "stopping axes gave us error code ", error_code

def SetVelocityToFactor(x_vel_fac,y_vel_fac, z_vel_fac, a_vel_fac, print_error=False):
	SetVelFac = Step4['LS_SetVelFac']
	x_vel_fac_c = ctypes.c_double(x_vel_fac)
	y_vel_fac_c = ctypes.c_double(y_vel_fac)
	z_vel_fac_c = ctypes.c_double(z_vel_fac)
	a_vel_fac_c = ctypes.c_double(a_vel_fac)
	error_code = ctypes.c_int32(-1)
	error_code = SetVelFac(x_vel_fac_c, y_vel_fac_c, z_vel_fac_c, a_vel_fac_c)
	if print_error or error_code != 0:
		print "we tried setting relative speed of ", x_vel_fac_c, y_vel_fac_c, " and we got erorr code ", error_code
		
def	GetVelocityFactor():
	GetVelFac = Step4['LS_GetVelFac']
	x_vel_fac = ctypes.c_double(0)
	y_vel_fac = ctypes.c_double(0)
	z_vel_fac = ctypes.c_double(0)
	a_vel_fac = ctypes.c_double(0)
	error_code = ctypes.c_int32(-1)
	error_code = GetVelFac(ctypes.byref(x_vel_fac),ctypes.byref(y_vel_fac),ctypes.byref(z_vel_fac),ctypes.byref(a_vel_fac))
	return array([x_vel_fac.value, x_vel_fac.value, x_vel_fac.value, x_vel_fac.value])
	if print_error or error_code != 0:
		print "we tried getting the velocity factor ", x_vel_fac_c, y_vel_fac_c, " and we got erorr code ", error_code
	
##########		Here are some functions written by me relating to the step engine control		##########
def CalcVelocity(sleep_time):
	t1 = clock()
	pos1 = GetPosition()
	sleep(sleep_time)
	t2 = clock()
	pos2 = GetPosition()
	vel_approx = (pos2 - pos1)/(t2-t1)
	print "pos2 is ", pos2, " pos 1 is ", pos1
	return vel_approx

def CalcSpeed(velocity):
	speed = sqrt(velocity[0]**2 + velocity[1]**2)
	return speed
	
def NormalizeVector(vector): # this should probably not be here but ... Normalizes a 2 long vector
	new_vec = array(vector)/sqrt(vector[0]**2 +vector[1]**2)
	return new_vec

def CalcSpeedError(time): ## Returns the relative error (1 = no error) for the SetSpeed command
	vel_fac = GetVelocityFactor()
	x_fac, y_fac = vel_fac[0], vel_fac[1]
	print "x_fac is ", x_fac, " and y_fac is ", y_fac, " max speed is set to ", 3./min(x_fac,y_fac)
	SetSpeed(3/x_fac,3/y_fac,0,0, max_speed=3./min(x_fac,y_fac) )
	t1 = clock()
	pos_pre = GetPosition()
	sleep(time)
	t2 = clock()
	pos_post = GetPosition()
	StopAxes()
	MoveToAbsolutePosition(pos_pre[0], pos_pre[1], 0,0, True)
	error = (pos_post[0] - pos_pre[0])/(3*(t2-t1))
	return error

def	SaveStepPos(options, timedata, extra_file=-1):
	if options.testing_disconnected:
		return 0
	t0 = clock()
	currentPosition = GetPosition()
	currentPosition = array([currentPosition[0], currentPosition[1]])
	print "current position is ", currentPosition, type(currentPosition)

	#print "getting pos took ", clock() - t0
	t_obj = localtime()
	t_ms  = time_now() - floor(time_now())
	t_tot = 0
	t_tot += t_obj.tm_mday*86400000
	t_tot += t_obj.tm_hour*3600000
	t_tot += t_obj.tm_min*60000
	t_tot += t_obj.tm_sec*1000
	t_tot += t_ms*1000
	currentTime 	= t_tot # Ths should be modified to whatever Teddy wants to have here.
	#print "getting time took ", clock() - t0
	if options.extra_file != -1 and os.path.exists(options.saving_directory):
		extra_file.write(to_str(currentTime, 13) + "\t" + to_str(currentPosition[0]) + "\t" + to_str(currentPosition[1]) + "\t 0.000000 \n")
	outfile.write(to_str(currentTime, 13) + "\t" + to_str(currentPosition[0]) + "\t" + to_str(currentPosition[1]) + "\t 0.000000 \n")
	#print "writing took ", clock() - t0
	pos_save_time = clock() - t0
	timedata.pos_save_total += pos_save_time
	return currentPosition 

def TerminateStepConnection(starting_left):
	StopAxes()
	SetVelocity(3, 3, 0, 0,3)
	if starting_left:
		MoveToAbsolutePosition(0,0,0,0,1) ## We assume that we are at the left inlet
	else:
		MoveToAbsolutePosition(-35,0,0,0,1) ## We assume that we are at the left inlet
	SetJoystickOn(True, True)
	Disconnect()

#def CloseFiles():
	
## Okay so I have done some experiments. Conclusions from today from what I have learnt:

# 1) Always start with the connect command, i use Connect Simple with mode 1
#    which means it is connecting using a com port. It seems our current com
#    port is nr 5. 
# 2) It seems setting velocity is not setting it off towards a direction but is the
#    velocity the engine will move to a position once instructed to move there. This
#    means the way to implement our engine has to be to set the target position far
#    away (probably locate the ends of the channel?) and then only switch target
#    once our particle has negative derivative. This might lead to some small 
#    complications down the line.
# 3) Don't forget to have your functions return an error code.
# 4) You will sporadically have 4004 errors, random communication errors with setup,
#    however if the issues are consistent, then you are most likely still open in 
#    another conversation channel. 
# 5) I will not be able to run the step controller at the same time that Anton runs
#    his step position meassurer. That should not be a huge deal as I should be able 
#    to implement that into my program in less than a day. 
# 6) Velocity of .4 is in the correct ballpart of the speed of the particles we've 
#    been using, and the length of the track is the ballpark of 40. I should examine 
#    this closer though.

## Further experiments: WRITE THIS LATER!!!!!!!
#ConnectSimple(1, "COM4", 9600, 1)
### Utility functions
#SetLanguage("ENG")
#FlushBuffer()

#SetVelocity(0.4,0.4,0,0.4)
#MoveToRelativePosition(-10,0,0,0,1)

#MoveToAbsolutePosition(5.0,5.0,1,1,1)
#sleep(0.2)
#print a
#b = GetPosition()
#print "Our position is ", b
#sleep(10)
#Disconnect()
# far felmeddelande ElnitlFACE
## Far felmeddelande: Keine Verbindung zur Steuerung
