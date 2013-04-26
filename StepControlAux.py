##### In this file are a number of functions that were implemented into StepControl.py but 
##### were made redundant or never actually needed. However it is possible they will find some future use. 
import ctypes
from time import sleep, clock
from numpy import array
from math import sqrt, copysign


Step4 = ctypes.WinDLL('C:/dllfolder/LStep4.dll')



def SetVelocitySingle(axis, axis_vel, print_error=False):
	SetVelSingle = Step4['LS_SetVelSingleAxis']
	axis_vel_c = ctypes.c_double(axis_vel)
	axis_c     = ctypes.c_int(axis)
	error_code= ctypes.c_int32(-1)	
	error_code = SetVelSingle(axis_c,axis_vel_c)


def GetVelocity(print_error=False):
	GetVel = Step4['LS_GetVel']
	x_vel_c = ctypes.c_double(2)
	y_vel_c = ctypes.c_double(2)
	z_vel_c = ctypes.c_double(2)
	a_vel_c = ctypes.c_double(2)	
	error_code= ctypes.c_int32(-1)
	error_code = GetVel(ctypes.byref(x_vel_c),ctypes.byref(y_vel_c),ctypes.byref(z_vel_c),ctypes.byref(a_vel_c))
	return [x_vel_c.value, y_vel_c.value, z_vel_c.value, a_vel_c.value]

def MoveToRelativePosition(X, Y, Z, A, wait, print_error=False):
	move_to_rel = Step4['LS_MoveRel']
	x_pos = ctypes.c_double(X)
	y_pos = ctypes.c_double(Y)
	z_pos = ctypes.c_double(Z)
	a_pos = ctypes.c_double(A)
	wait_bool  = ctypes.c_int(wait)
	error_code = ctypes.c_int32(-1)
	error_code = move_to_rel(x_pos,y_pos, z_pos, a_pos, wait_bool)
	if print_error or error_code != 0:
		print "Our error code for moving was ", error_code

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


def FlushBuffer(print_error=False):
	flush_buffer = Step4['LS_FlushBuffer']
	useless = ctypes.c_int(0)
	error_code = ctypes.c_int32(-1)
	error_code = flush_buffer(useless)
	if print_error or error_code != 0:
		print "flushing gave us error code ", error_code

def SetLanguage(language, print_error=False):
	set_language = Step4['LS_SetLanguage']
	language_c = ctypes.c_char_p(language)
	error_code = ctypes.c_int32(-1)
	error_code = set_language(language_c)
	if print_error or error_code != 0:
		print "language changing gave us error code ", error_code
