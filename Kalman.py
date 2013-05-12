import numpy as np

class Kalman():
	def __init__(self, fps_max, going_right, middle):
		## THINGS FOR KALMAN FILTER
		## EXPERIMENTAL
		self.dt = 1/fps_max
		dt		= self.dt
		self.A = np.mat([[1,dt,0,0],[0,1,0,0],[0,0,1,dt],[0,0,0,1]])
		self.B = np.mat([[dt,0,0,0],[0,1,0,0],[0,0,dt,0],[0,0,0,1]])
		self.H = np.identity(4)#*step_2_pixel # Which should we choose here?...
		self.P = np.identity(4) # This changes over time so we are not too worried.
		self.Q = np.identity(4)*0.01 # We are pretty confident it our model.. maybe foolishly so!
		self.R = np.identity(4)*0.010  # we are a fair bit more uncertain about this...
		self.S = np.identity(4)
		self.I = np.identity(4)
		self.x_old = np.mat([middle[0], 0.5*(1-going_right), middle[1], 0]).transpose()
		self.control = np.mat([0,0,0,0]).transpose()
		
	def predict(self, state, step_2_pixel):
		dt 			= self.dt
		self.control= np.mat([state.corr_vec[0]*dt,state.corr_vec[0], state.corr_vec[1]*dt, state.corr_vec[1]])
		self.control = self.control.transpose()*step_2_pixel
		print "A is ", self.A.shape, " x_old is ", self.x_old.shape
		print "B is ", self.B.shape, " control is ", self.control.shape
		self.x_pred = self.A*self.x_old + self.B*self.control
		self.P_pred = self.A*self.P*self.A.transpose() + self.Q
	
	def update(self, state):  ## I am pretty sure this uses wikipedia notations
		x_meas = [state.pos_approx[0], state.simple_vel[0],state.pos_approx[1], state.simple_vel[1]]
		x_meas = np.array(x_meas).transpose()
		self.y = x_meas - (self.H*self.x_pred)
		self.S = self.H * self.P_pred * self.H.transpose()  + self.R
		self.K = self.P_pred*self.H.transpose()*np.linalg.inv(self.S)
		self.x_est = self.x_pred + (self.K*self.y)
		self.P_est = (self.I - self.K*self.H)*self.P_pred
		
