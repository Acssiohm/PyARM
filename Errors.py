class Error():
	"""docstring for Errors"""
	def __init__(self, typeERR, msg, line, line_content = "", filename = ""):
		self.type = typeERR
		self.msg = msg
		self.line = line
		self.file = filename
		self.content = line_content

	def RAISE(self):
		print()
		print(f'{self.type} : {self.msg}')
		print(f'File : {self.file}\t\tline : {self.line}'  )
		if self.content :
			print('--> "' + self.content + '"')		
		quit()