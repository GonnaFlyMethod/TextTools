import re
import itertools


class Lingvuo:

	@staticmethod
	def version() -> str:
		return '0.1'

	def __init__(self, text: str):
		self.path = text
		self.text = text  # Contains custom property
		self._num_of_letters = len(self.text)

	def __str__(self):
		return self.text

	def __repr__(self):
		msg = None
		if len(self.text) >= 20:
			msg = '<TEXT: %s..., '\
			      'lenght: %d>' % (self.text[:21], len(self.text))
		else:
			msg = '<TEXT: %s... lenght: %d>' % (self.text, len(self.text))
		return msg

	def __eq__(self, other):
		if other.__class__ == Lingvuo:
			return self.text == other.text
		elif isinstance(other, int):
			return len(self.text) == other
		elif isinstance(other, str):
			return self.text == other
		else:
			raise ValueError()

	def __ne__(self, other):
		if other.__class__ == Lingvuo:
			return self.text != other.text
		elif isinstance(other, int):
			return len(self.text) != other
		elif isinstance(other, str):
			return self.text != other
		else:
			raise ValueError()

	@property
	def text(self):
		return self._text

	@text.setter
	def text(self, value):
		if not isinstance(value, str):
			raise ValueError()
		
		with open(value, 'r') as f:
			text = ''
			for line in f:
				clean_line = line.rstrip('\n')
				for letter in clean_line:
					text += letter

		self._text = text

	def get_number_of_letters(self) -> int:
		counter:int = 0

		with open(self.path, 'r') as file:
			for line in file:
				clean_line = line.strip('\n')
				for l in clean_line:
					is_not_space:bool = l.isspace()
					if not is_not_space:
						counter += 1
		return counter

	def get_num_of_certain_letter(self, letter: str) -> int:
		counter:int = 0

		with open(self.path, 'r') as f:
			for line in f:
				clean_line = line.strip('\n')

				for l in clean_line:
					if letter == l:
						counter += 1
		return counter

	def get_num_of_spaces(self) -> int:
		counter: int = 0

		with open(self.path, 'r') as f:
			new_text = list(f)
			cleaned_text = []
			for line in new_text:
				stripped_line = line.rstrip('\n')
				cleaned_text.append(stripped_line)

			for line in cleaned_text:
				for letter in line:
					if letter.isspace():
						counter += 1
		return counter

	def get_while(self, word: str) -> int:
		with open(self.path, 'r') as f:
			string = ''
			text = ''
			for line in f:
				text += line

			for letter in itertools.takewhile(lambda x: x != word, text):
				string += letter

		return string

	def drop_while(self, word: str, type_='equals') -> int:
		with open(self.path, 'r') as f:
			string = ''
			text = ''
			for line in f:
				text += line

			for letter in itertools.dropwhile(lambda x: x != word, text):
				string += letter
		return string

	def text_generator(self, type_='line') -> str:
		if type_ == 'line':
			with open(self.path, 'r') as f:
				for line in f:
					yield line
		elif type_ == 'letter':
			with open(self.path, 'r') as f:
				for line in f:
					for l in line:
						yield l
		else:
			raise ValueError()

	def get_text_mirror(self, text: str, display:bool =True) ->str:
		# ...
		pass


class Re(Lingvuo):

	def cotains_pattern(self, regex_pattern):
		with open(self.path, 'r') as f:
			string = ''

			for line in f:
				for letter in line:
					string += letter
		regex_pattern = r'' + regex_pattern
		pattern = re.compile(regex_pattern)
		is_contains = pattern.finditer(self.text)

		for i in is_contains:
			print(i)

	def get_patterns(self, regex_pattern):
		with open(self.path, 'r') as f:
			string = ''

			for line in f:
				for letter in line:
					string += letter
		regex_pattern = r'' + regex_pattern
		pattern = re.compile(regex_pattern)
		is_contains = pattern.finditer(self.text)

		return is_contains

C = Re('example.txt')
C.cotains_pattern('a')
