import re
import itertools
import requests
import json
import pprint

class Text:

	@staticmethod
	def version() -> str:
		return '0.2'

	def __init__(self, text: str):
		self.path = text
		self.text = text  # Contains custom property, initial text
		self._num_of_letters = len(self.text)
		self._updated_text = None

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
				for letter in line:
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

	def update_text_file(self, value:str):
		with open(self.path, 'w') as f:
			f.write(value)


class Re(Text):

	HTML_TAGS = r'<\/?\w+(\s+)?[^>]*>'
	LINKS = r'[\s|\n]{0}(https?://)?(www\.)?' \
		      r'[A-Za-z0-9._]+\.\w+[^\s{}\[\]\{\}]+'
	PHONE_NUMBERS = r'\+?\d{1,3}\s?([-(])\d{2,3}([-)])\s?\d+-?\d+'
	SPORT_SCORE = r'\d{1,3}:\d{1,3}'

	@classmethod
	def get_regex(cls) -> dict:
		reg_ex:dict = {
			'HTML TAGS':cls.HTML_TAGS,
			'LINKS': cls.LINKS,
			'PHONE_NUMBERS': cls.PHONE_NUMBERS,
			'SPORT_SCORE': cls.SPORT_SCORE
		}

		return reg_ex

	def _return_result(self, re_objects, display=False) -> list:
		full_display = []
		for o in re_objects:
			spans:tuple = o.span()
			start:int = spans[0]
			end:int = spans[1]
			new_list = o.group(), spans
			full_display.append(new_list)

		if display:
			for el, position in full_display:
				print(f'Element: {el}, position: {position}')
		else:
			pass

		return full_display

	def _prepare_string_for_re(self, regex_pattern:str) -> str:
		reg_def = r''
		regex_pattern = reg_def + regex_pattern
		return regex_pattern

	def get_first_match(self, regex_pattern: str, display=False):
		regex_pattern = self._prepare_string_for_re(regex_pattern)
		match = re.search(regex_pattern, self.text)
		res = self._return_result([match], display=display)

		return res

	def check_fullmatch(self, regex_pattern: str, display=False) -> bool:
		regex_pattern = self._prepare_string_for_re(regex_pattern)
		match = re.fullmatch(regex_pattern, self.text)
		if match: return True
		return False

	def get_all_matches(self, regex_pattern:str, display=False) -> list:
		regex_pattern = self._prepare_string_for_re(regex_pattern)
		pattern = re.compile(regex_pattern)
		matches = pattern.finditer(self.text)
		res = self._return_result(matches, display=display)
		return res

	def get_list_of_matches(self, regex_pattern: str) -> list:
		regex_pattern = self._prepare_string_for_re(regex_pattern)
		matches = re.findall(regex_pattern, self.text)
		return matches

	def get_words_with_x_letters(self, num_of_letters: int,
		                         display=False) -> list:
		edge = r'\b'
		experssion = edge + '\w' + '{' + f'{num_of_letters}' + '}' + edge
		pattern = re.compile(experssion)
		matches = pattern.finditer(self.text)
		res:list = self._return_result(matches, display=display)
		return res

	def split(self, regex_pattern: str, maxsplit=0) -> list:
		regex_pattern = self._prepare_string_for_re(regex_pattern)
		text:list = re.split(regex_pattern, self.text, maxsplit=maxsplit)
		return text

	def replace_all_matches(self, regex_pattern: str, repl, count=0) -> str:
		regex_pattern = self._prepare_string_for_re(regex_pattern)
		replaced:list = re.sub(regex_pattern, repl, self.text, count=count)
		return replaced

	def find_html_tags(self, display=False) -> list:
		matches = re.finditer(self.HTML_TAGS, self.text)
		res = self._return_result(matches, display=display)
		return res

	def find_links(self, display=False) -> list:
		matches = re.finditer(self.LINKS, self.text)
		res = self._return_result(matches, display=display)
		return res

	def find_phone_numbers(self, display=False) -> list:
		matches = re.finditer(self.PHONE_NUMBERS, self.text)
		res = self._return_result(matches, display=display)
		return res

class Word(Re):

	def __init__(self, word):
		self.word = word

	@property
	def word(self):
		return self._word

	@word.setter
	def word(self, value):
		assert isinstance(value, str) == True

		self._word = value.lower()
	
	# REST API
	def get_usage(self, display=False) -> list:
		apiurl = 'https://lt-collocation-test.herokuapp.com/todos/'\
		         '?query=%s&lang=en' % self.word

		response = requests.get(apiurl)
		json_data = json.loads(response.text)
		examples:list = []
		for i in json_data:
			ex = i['examples']
			for e in ex:
				if isinstance(e, str):
					clean_line = re.sub(self.HTML_TAGS, '', e)
					examples.append(clean_line)
		
		if display:
			for num, ex in enumerate(examples):
				print(f'{num + 1}) {ex}')
		return examples

	def predict_nationality_if_name(self, display=False):
		api = f'https://api.nationalize.io/?name={self.word}'
		response = requests.get(api)
		get_json:dict = json.loads(response.text)
		name = self.word.capitalize()

		if display:
			asteriks = '*' * 5
			head = asteriks + f' [{name}] ' + asteriks
			print(head)

			country = get_json['country']
			for c in country:
				print(f"Country id: {c['country_id']}")
				probability_raw = round(c['probability'] * 100, 2)
				probability = str(probability_raw) + ' %'
				print(f'Probability {probability}')
				print('_' * len(head))
		return get_json


word = Word('Sasha')
word.predict_nationality_if_name(display=True)