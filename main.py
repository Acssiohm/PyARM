import sys
from time import *
from random import *
from ctypes import *

from Parser import Parser
from Language import Language
class Computer():
	def __init__(self, nb_bits, ram_size, nb_regs, frequency = -1):
		self. language = Language(ram_size, nb_regs, nb_bits)
		self.period = 1/frequency
		self.bus = Memory_cell(nb_bits)

		self.RAM = RAM(ram_size, nb_bits, self.bus)
		self.Regs = Registers(nb_regs, nb_bits, self.bus)
		self.PC = PointerCounter(0)
		self.CU = ControlUnit(0, self.bus)
		self.ALU = ALU(None)
		

	def Program (self, program):
		parse = Parser( program, self.language)
		program = parse.FinalCode
		print("Programming...")
		for adress, information in enumerate(program) :
			self.RAM.memory[adress].set(information)
		print("RAM is programmed !")
		return adress

	def run(self, n):
		for _ in range(n):
			self.bus.set(self.PC.get())
			self.RAM.MAR_IN()
			self.RAM.RAM_OUT()




class ControlUnit():
	"""docstring for ControlUnit"""
	def __init__(self, size, bus):
		self.size = size
		self.bus = bus


		
		
		
class ALU():
	"""docstring for ALU"""
	def __init__(self, arg):
		super(ALU, self).__init__()
		self.arg = arg

class RAM():
	"""docstring for RAM"""
	def __init__(self, size, cell_size, bus):
		self.memory = [Memory_cell(cell_size) for _ in range(size)]
		self.MAR = Buffer(size, bus)
		self.MBR = Buffer(cell_size, bus)

	def RAM_OUT(self):
		adress = self.MAR.read()
		memory_content = self.memory[adress].get()
		self.MBR.write(memory_content)
		self.MBR.setBus()

	def RAM_IN(self):
		adress = self.MAR.read()
		self.MBR.getBus()
		new_content = self.MBR.read()
		self.memory[adress].set(new_content)

	def MAR_IN(self):
		self.MAR.getBus()

class Buffer():
	"""docstring for Buffer"""
	def __init__(self, size, bus):
		self.value = c_uint32(0)
		self.bus = bus

	def setBus(self):
		self.value = self.bus.get()

	def getBus(self):
		self.bus.set(self.value)

	def read(self):
		return self.value.value

	def write(self, val):
		self.value = val
		
class Registers():
	"""docstring for Registers"""
	def __init__(self, Registers_number, Registers_size, bus):
		self.regs = [Memory_cell(Registers_size) for _ in range(Registers_number)]
		self.bus = bus

	def getInBus(self, register):

		self.bus.set(seblf.regs[register].get())

	def setFromBus(self, register):
		self.regs[register].set(self.bus.get())
		
class Memory_cell():
	"""docstring for Reg"""
	def __init__(self, size):
		self.value = c_uint32(0)
		self.size = size

	def get(self):
		return self.value.value
	
	def set(self, value):
		self.value = c_uint32(value)

class PointerCounter():
	"""docstring for PointerCount"""
	def __init__(self, bus, start = 0 ):
		self.count = start
		self.bus = bus

	def incrementer(self):
		self.count += 1

	def PC_OUT(self):
		self.bus.set(self.count)
	
	def PC_IN(self):
		self.count = self.bus.get()
		
test_string = "\n".join(["LDR R0, Michel", " Michel:/jgcjhcgazhdcxdc", "\t    /,gzevcjhvezc"])
if len(sys.argv) > 1 :
	file = open(str(sys.argv[1]), 'r')
	test_string = file.read()
	file.close()

comp = Computer(32, 200, 12)
comp.Program(test_string)