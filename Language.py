class Language():
	"""docstring for Language"""
	def __init__(self, RAM, Registers, bitsPerInstruction ):

		self.Rn = "R"
		self.opr = "op"
		self.memRef = "mem"
		self.adr = "lbl"
		self.out = "out"
		self.inp = "in"

		self.Instructions = {"LDR":[self.Rn, self.memRef], "STR":[self.Rn, self.memRef],
		"ADD":	[self.Rn, self.Rn, self.opr], "SUB":[self.Rn, self.Rn, self.opr],
		"MOV":	[self.Rn, self.opr],"CMP":[self.Rn, self.opr],
		"B":	[self.adr],"BEQ":[self.adr],"BNE":[self.adr],"BGT":[self.adr],"BLT":[self.adr],
		"AND":	[self.Rn, self.Rn, self.opr],"ORR":[self.Rn, self.Rn, self.opr],"EOR":[self.Rn, self.Rn, self.opr],
		"MVN":	[self.Rn, self.opr],
		"LSL":	[self.Rn, self.Rn, self.opr],"LSR":[self.Rn, self.Rn, self.opr],
		"HALT":	[],
		"INP":	[self.Rn, self.inp], "OUT" :[self.Rn, self.out],
		"DAT":	[self.adr]}
		
		self.inputAdresses = [2, 4, 5, 8]
		self.outputAdresses = [4, 5, 6, 7, 8]
		
		self.instrs = list(self.Instructions.keys())
		# print(self.instrs, len(self.instrs), len(self.instrs).bit_length() )
		self.hexadecimal = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
	
		self.command_bit_size = (len(self.instrs) + 1).bit_length()
		self.Registers_bit_Quantity = (Registers).bit_length()
		self.Instruction_bit_Size = bitsPerInstruction
		self.RAM_bit_Size = (RAM).bit_length()
		self.Max_input_bits = max(self.inputAdresses).bit_length()
		self.Max_output_bits = max(self.outputAdresses).bit_length()
		
		self.param_size = {
			self.Rn : self.Registers_bit_Quantity,
			self.opr : self.Instruction_bit_Size - 2*self.Registers_bit_Quantity - 1 ,
			self.memRef : self.RAM_bit_Size + self.Registers_bit_Quantity + 1 ,
			self.adr : self.RAM_bit_Size, 
			self.out : self.Max_input_bits,
			self.inp : self.Max_output_bits
		}
		self.verif_function = {
				self.Rn : self.isRegister,
				self.opr : self.isOperand,
				self.memRef : self.isMemoryRef,
				self.adr : self.isAdress,
				self.out : self.isOutputAdress,
				self.inp : self.isInputAdress	
		}

		self.encode_function = {
				self.Rn : self.encodeRegister,
				self.opr : self.encodeOperand,
				self.memRef : self.encodeMemoryRef,
				self.adr : self.encodeAdress,
				self.out : self.encodeAdress,
				self.inp : self.encodeAdress
		}

		
	def resize_number(self, number, bit_size):
		return number & (2**bit_size - 1)

	def encodeRegister ( self, registre):
		return int(registre.removeprefix("R")) & (2**self.param_size[self.Rn] -1)
	
	def encodeOperand(self, opr):
		return ( int(opr[1:])<<1 | (opr[0] == "R") ) & (2**self.param_size[self.opr] -1)

	def encodeMemoryRef(self, ref):
		if "+" in ref :
			refR, refA = ref.split('+')
			return  ( self.encodeRegister(refR) << (self.param_size[self.adr]+1) ) | (self.encodeAdress(refA)  ) << 1 | 1
		else :
			return (self.encodeAdress(ref) ) << 1
	
	def encodeAdress(self, adr):
		return int(adr) & (2**self.param_size[self.adr] -1)

	def paramsCode(self, instruction, params):
		params_code = 0
		for n, param in enumerate(params):
			param_type = self.Instructions[instruction][n]
			param_size = self.param_size[param_type]
			params_code |= self.encode_function[param_type]( param )
			params_code <<= self.param_size[param_type]
			# print(param_type, param_size, params_code)
		return params_code

	def InstructionCode (self, instruction):
		if instruction in self.instrs :
			return self.instrs.index(instruction) + 1
		return None

	def Assemble(self, code):
		assembled = []
		for instruction in code : 
			command = self.InstructionCode(instruction[0])
			params = self.paramsCode(*instruction)
			# print(bin(command),self.Instruction_bit_Size, self.command_bit_size, (command << (self.Instruction_bit_Size - self.command_bit_size)).bit_length() )
			assembled.append((command << (self.Instruction_bit_Size - self.command_bit_size)) | params)
		return assembled


	def isValidCode(self, code, labels):
		better_code = []
		for n, command in enumerate(code) :
			isCorrect, toCorrect = self.isValidCommand(command, labels)
			if not isCorrect :
				return False, toCorrect , n
			better_code.append(toCorrect)
		return True, better_code, None

	def isInputAdress(self, adr):
		
		return int(adr) in self.inputAdresses, adr

	def isOutputAdress(self, adr):

		return int(adr) in self.outputAdresses, adr

	def isValidCommand(self, command, labels):
		if len(command) != 2 :
			return
		if self.isInstruction(command[0]):
			verif_params = self.Instructions[command[0]]
			params = command[1]
			if len(params) == len(verif_params):
				correctsV = []
				for verif, param in zip(verif_params, params):
					isverif, correctV = self.verif_function[verif](param, labels = labels)
					if not isverif:
						return False, correctV
					correctsV.append(correctV)
				return True, [command[0], correctsV]
		return False, f"{command} n'est pas une instruction reconnue"

	def isInstruction(self, command, **kwargs):

		return command.upper() in self.Instructions.keys()

	def isOperand(self, operand, **kwargs):
		operand = operand.strip()
		isconst, correctC = self.isConstant(operand, **kwargs)
		isreg, correctR = self.isRegister(operand, **kwargs)

		if isconst :	return True, correctC
		elif isreg :	return True, correctR
		else :			return False, correctC + "  OR  " + correctR 

	def isMemoryRef(self, ref, **kwargs):
		ref = ref.strip()
		isadr, correctA = self.isAdress(ref, **kwargs)
		isindr, correctI = self.isIndirectAdressing(ref, **kwargs)
		if isadr :		return True , correctA
		elif isindr : 	return True, correctI
		else :			return False, correctA + "  ET  " + correctI 

	def isIndirectAdressing(self, ref, **kwargs):
		if len(ref) > 2 and ref[0] == "[" and ref[-1] == "]":
			ref = ref[1:-1].strip()
			if "+" in ref :
				reg, adr = ref.split("+", 1)
				isreg, correctR = self.isRegister(reg, **kwargs)
				isadr, correctA = self.isAdress(adr, **kwargs) 
				if isreg and isadr :
					return True, correctR+"+"+correctA
				return False, correctA + "  AND  " + correctR
			return self.isRegister(ref)
		return False, f"{ref} n'est pas une adresse indirecte valide"

	def isHex(self, number):
		if number.startswith("0X"):
			hexConstant = number.removeprefix("0X")
			for digit in hexConstant :
				if digit not in self.hexadecimal:
					return False
			return True
		return False

	def isConstant(self, number, **kwargs):
		number = number.strip()
		if number[0] == "#" and len(number) > 1 :
			constant = number[1:]
			if constant.isdecimal() :
				return True, number 
			elif constant.startswith("0X"):
				if self.isHex(constant):
					return True, "#"+str(int(constant, 16))
				else :
					return False, "There is "+digit+" in the hexadecimal number : '"+ number + "'"
			elif constant.startswith("0B"):
				binary_constant =  constant.removeprefix("0B")
				for digit in binary_constant :
					if digit not in {"0", "1"}:
						return False, "There is "+digit+" in the binary number : '"+ number + "'"
				return True, "#"+str(int(binary_constant,2))
		return False, "This is not a constant : " + number

	def isRegister(self, reg, maxi = -1 , **kwargs):
		reg = reg.strip()
		if len(reg) > 1 and reg[0] == "R" :
			reg_n = reg[1:]
			if reg_n.isdecimal() :
				if maxi == -1 or maxi >= int(reg_n) :
					return True, reg
		return False ,(f"{reg} n'est pas un registre")

	def isAdress(self, adr, **kwargs):
		labels = kwargs.get("labels")
		if adr.strip().isdecimal():		return True, adr.strip() 
		elif self.isHex(adr) :			return True, str(int(adr, 16))
		elif adr in labels:				return True, str(labels[adr])
		else : 							return False, f"{adr} n'est pas une adresse valid"
