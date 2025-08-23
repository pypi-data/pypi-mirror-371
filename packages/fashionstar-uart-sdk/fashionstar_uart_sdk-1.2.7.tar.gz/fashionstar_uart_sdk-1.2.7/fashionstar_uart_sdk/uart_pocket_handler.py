import serial
from .uservo import *

class StopOptions:
	mode={
		"locked" : 0x10,
		"unlocked" : 0x11,
		"damping" : 0x12
		}
	# def __init__(self, str_mode:str):
	# 	return self.mode(str_mode)
	def str2int(self, str_mode:str):
		return self.mode[str_mode]

# class SynchrousInstruction:
# 	mode={
# 		"single_turn_position_control_mode1" : 0x10,
# 		"single_turn_position_control_mode2" : 0x11,
# 		"single_turn_position_control_mode3" : 0x12,
		
# 		}
# 	def str2int(self, str_mode:str):
# 		return self.mode(str_mode)

class Monitor_data:
	id :int
	current_position :float
	power:int
	voltage :int
	current:int
	temperature :float
	status:int
	def __init__(self, id:int, current_position:float, power:int, voltage:int, current:int, temperature:float, status:int):
		self.id = id
		self.current_position = current_position
		self.power = power
		self.voltage = voltage
		self.current = current
		self.temperature = temperature
		self.status = status
	def __str__(self):
		return f"Motor {self.id}:\n\tCurrent Position: {self.current_position}\n\tPower: {self.power}\n\tVoltage: {self.voltage}\n\tCurrent: {self.current}\n\tTemperature: {self.temperature}\n\tStatus: {self.status}"
		





class PocketHandler(UartServoManager):

	def __init__(self, port_name:str, baudrate:int):
		uart = serial.Serial(port=port_name, baudrate=baudrate,parity=serial.PARITY_NONE, stopbits=1,bytesize=8,timeout=0)
		super().__init__(uart)
		self.min_position_limit = [-1024*360.0 for i in range(255)]
		self.max_position_limit = [1024*360.0 for i in range(255)]

		self.is_open = False
		self.write={
			"Operating_Mode":None,
			"Present_Position":self.ReadCurrentPosition_EX,
			"Min_Position_Limit":self.SetMinPositionLimit,
			"Max_Position_Limit":self.SetMaxPositionLimit,
			"Stop_On_Control_Mode":self.StopOnContorlMode,
		}
		self.sync_read={
			"Monitor":self.SyncServoSonitor
		}
		self.sync_write={
		}

		if self.uart.is_open:
			self.is_open = True
		else:
			self.is_open = False

	def SetMinPositionLimit(self,id:int,limit:float):
		self.min_position_limit[id] = limit
	
	def SetMaxPositionLimit(self,id:int,limit:float):
		self.max_position_limit[id] = limit

	def PositionControl(self,id:int,target_position:float,motion_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power)
	
	def PositionControl_TimeBased(self,id:int,target_position:float,motion_time:int,accel_time:int,decel_time:int,power:int=0):		
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_SpeedBased(self,id:int,target_position:float,motion_speed:int,accel_time:int,decel_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,voltage = motion_speed,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_EX(self,id:int,target_position:float,motion_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power)
	
	def PositionControl_TimeBased_EX(self,id:int,target_position:float,motion_time:int,accel_time:int,decel_time:int,power:int=0):		
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_SpeedBased_EX(self,id:int,target_position:float,motion_speed:int,accel_time:int,decel_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,voltage = motion_speed,power = power,t_acc=accel_time,t_dec=decel_time)

	def ReadCurrentPosition(self,id:int):
		return self.query_servo_angle(servo_id=id)
	
	def ReadCurrentPosition_EX(self,id:int):
		return self.query_servo_mturn_angle(servo_id=id)

	def ResetLoop(self,id:int):
		return self.reset_multi_turn_angle(servo_id=id)

	def DampingControl(self,id:int,power:int):
		return self.set_damping(servo_id=id,power=power)
	
	def StopInstructions(self,id:int,mode:str,power:int):
		return self.stop_on_control_mode(servo_id=id,mode=StopOptions(mode),power=power)
	
	def StopOnContorlMode(self,id:int,mode:str,power:int):
		return self.stop_on_control_mode(servo_id=id,mode=StopOptions(mode),power=power)



	############
	def SyncServoSonitor(self, motors:dict[str,id])-> dict[str, Monitor_data]:
		ids = [motors[id] for id in motors]
		self.send_sync_servo_monitor(servo_ids=ids)

		monitor_datas:dict[str, Monitor_data] = {}
		for motor in motors:
			id = motors[motor]
			data = Monitor_data(id,
								self.servos[id].angle_monitor, 
								self.servos[id].power, 
								self.servos[id].voltage, 
								self.servos[id].current, 
								self.servos[id].temp, 
								self.servos[id].status)
			monitor_datas[motor] = data
		return monitor_datas


	# def send_sync_anglebyinterval(self, command_id, servo_num, command_data_list):

	# 	return super().send_sync_anglebyinterval(command_id, servo_num, command_data_list)
	
	# ####写法1
	# def basicSingleTurnPositionControl
	# def advancedSingleTurnPositionControl_TimeBased
	# def advancedSingleTurnPositionControl_SpeedBased
	
	# def basicMultiTurnPositionControl
	# def advancedMultiTurnPositionControl_TimeBased
	# def advancedMultiTurnPositionControl_SpeedBased

	# ####写法2
	# def singleTurnPositionControl
	# def singleTurnPositionControl_TimeBased
	# def singleTurnPositionControl_SpeedBased

	# def MultiTurnPositionControl
	# def MultiTurnPositionControl_TimeBased	
	# def MultiTurnPositionControl_SpeedBased

	# ####写法3
	# def PositionControl		
	# def PositionControl_TimeBased		
	# def PositionControl_SpeedBased
	
	# def PositionControl_EX
	# def PositionControl_TimeBased_EX	
	# def PositionControl_SpeedBased_EX