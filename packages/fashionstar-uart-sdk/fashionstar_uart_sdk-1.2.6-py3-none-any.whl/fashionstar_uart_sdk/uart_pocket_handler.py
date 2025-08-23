import serial
from uservo import *

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

class SynchrousInstruction:
	mode={
		"single_turn_position_control_mode1" : 0x10,
		"single_turn_position_control_mode2" : 0x11,
		"single_turn_position_control_mode3" : 0x12,
		
		}
	def str2int(self, str_mode:str):
		return self.mode(str_mode)



class PocketHandler(UartServoManager):

	def __init__(self, port_name:str, baudrate:int):
		uart = serial.Serial(port=port_name, baudrate=baudrate,parity=serial.PARITY_NONE, stopbits=1,bytesize=8,timeout=0)
		super.__init__(uart)

		self.function={
			"Operating_Mode":None,
			"Present_Position":self.query_servo_angle,

		}

	def PositionControl(self,id:int,target_position:float,motion_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power)
	
	def PositionControl_TimeBased(self,id:int,target_position:float,motion_time:int,accel_time:int,decel_time:int,power:int=0):		
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_SpeedBased(self,id:int,target_position:float,motion_speed:int,accel_time:int,decel_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,velocity = motion_speed,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_EX(self,id:int,target_position:float,motion_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power)
	
	def PositionControl_TimeBased_EX(self,id:int,target_position:float,motion_time:int,accel_time:int,decel_time:int,power:int=0):		
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_SpeedBased_EX(self,id:int,target_position:float,motion_speed:int,accel_time:int,decel_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,velocity = motion_speed,power = power,t_acc=accel_time,t_dec=decel_time)

	def ReadCurrentPosition(self,id:int):
		return self.query_servo_angle(servo_id=id)
	
	def ReadCurrentPosition_EX(self,id:int):
		return self.query_servo_mturn_angle(servo_id=id)

	####


	def resetLoop(self,id:int):
		return self.reset_multi_turn_angle(servo_id=id)

	def dampingControl(self,id:int,power:int):
		return self.set_damping(servo_id=id,power=power)
	
	def stopInstructions(self,id:int,mode:str,power:int):
		return self.stop_on_control_mode(servo_id=id,mode=StopOptions(mode),power=power)
	
	def synchronousInstruction():
		return 
	
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