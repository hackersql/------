class Output:
	def __init__(self):
		self.output_text ="+--------------------------------------------------+\n"
		self.output_text+="|   LuanMap V2.0  Code By Luan lu4n.com            |\n"
		self.output_text+="|                         Luan@Shepi.Org           |\n"
		self.output_text+="+--------------------------------------------------+\n"
	def print_output(self):
		print self.output_text
	def create_table(self,count):
		self.max_length_list = [1]*count
		self.cache_lists = []
	def add_line(self,columns):
		for index,col in enumerate(columns):
			if self.max_length_list[index] < len(col):
				self.max_length_list[index] = len(col)
		self.cache_lists.append(columns)
	def end_table(self):
		if self.cache_lists != []:
			max_length_table = sum(self.max_length_list) + len(self.max_length_list)*2 + 1
			for index,columns in enumerate(self.cache_lists):
				if index < 2:
					self.output_text += '+' + '+'.join(map(lambda x: '-'*(x+2), self.max_length_list)) + '+\n'
				self.output_text += '| '
				for _index,col in enumerate(columns):
					if len(col) < self.max_length_list[_index]:
						col += ' '*(self.max_length_list[_index]-len(col))
					self.output_text += col
					self.output_text += ' | '
				self.output_text.rstrip()
				self.output_text += '\n'
			self.output_text += '+' + '+'.join(map(lambda x: '-'*(x+2), self.max_length_list)) + '+\n'
			self.cache_lists = []