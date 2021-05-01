from Language import Language
from Errors import Error
class Parser():
	"""docstring for Parser"""
	def __init__(self, Program, ASM_Language):
		self.ASM = ASM_Language
		print("Parsing....")
		self.Program = Program.upper()
		self.commentSymboles = {"/", ";"}
		self.labelSymbol = ":"
		self.ProgramLines = self.parseLines()
		print("Remove comments...")
		self.uncommentedProgram = self.RemoveComments()
		print("Remove labels...")
		self.unLabeledProgram, self.labels = self.getLabels()
		self.programCommands = self.parse()
		print("Assembling...")
		self.FinalCode = self.Compile()
		print("Assembled !")

	def parseLines(self):

		return self.Program.split("\n")

	def RemoveComments(self):
		ProgramWithoutComments = []

		for n, line in enumerate(self.ProgramLines):
			commIdx = None
			for comSymb in self.commentSymboles:
				if comSymb in line :
					idxComSymb = line.index(comSymb)
					if commIdx is None or commIdx > idxComSymb:
						commIdx = idxComSymb
			if commIdx is None :
				if line.strip() :
					ProgramWithoutComments.append(line.strip())
			else :
				new_line = line[:commIdx].strip()
				if new_line :
					ProgramWithoutComments.append(new_line)
		return ProgramWithoutComments

	def getLabels(self):
		programWithoutLabels = []
		Labels = {}
		line_number = 0
		for line in self.uncommentedProgram :
			line_rest = None 
			if self.labelSymbol in line :
				label, line_rest  = line.split(self.labelSymbol, 1)
				Labels[label] = line_number
				if line_rest :
					programWithoutLabels.append(line_rest)
					line_number += 1
			else :
				programWithoutLabels.append(line)
				line_number += 1

		return programWithoutLabels, Labels

	def parse(self):
		parsedProgram = []
		for n, line in enumerate(self.unLabeledProgram):
			command = []
			if " " in line :
				instr, paramstr = line.split(" ", 1)
				paramstr = paramstr.replace(" ", "")
			else :
				instr = line.strip()
				paramstr = ""
			
			# for label in self.labels.keys() :
			# 	if label in paramstr :
			# 		paramstr = paramstr.replace(label, str(self.labels[label]) )

			if "," in paramstr :
				params = paramstr.split(",")
			elif paramstr :
				params = [paramstr.strip()]
			else :
				params = []
			command.append(instr)
			command.append(params)
			parsedProgram.append(command)
		return parsedProgram

	def Compile(self):
		# print(self.labels)
		correct, corrected, line = self.ASM.isValidCode(self.programCommands, self.labels)
		if not correct  :
			error = Error("Invalid Instruction", corrected,line,str(self.programCommands[line]), "test.asm")
			error.RAISE()
		else :
			return self.ASM.Assemble(corrected)

