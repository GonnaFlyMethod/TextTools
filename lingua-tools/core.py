import re
import itertools
import requests
import json
import pprint
import asyncio
from aiohttp import ClientSession
from _async import async_HTTP_request

import time

class Text:

	@staticmethod
	def version() -> str:
		return '0.0.5'

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

	def find_sport_score(self, display=False) -> list:
		matches = re.finditer(self.SPORT_SCORE, self.text)
		res = self._return_result(matches, display=display)
		return res


class Word(Re):

	def __init__(self, word):
		self.word = word
		self._word_for_api = self._set_value_for_api_requests(self.word)

	@property
	def word(self) -> str:
		return self._word

	@word.setter
	def word(self, value):
		assert isinstance(value, str) == True
		self._word = value.lower()

	def _set_value_for_api_requests(self, value) ->str:
		splitted_value = value.split()
		clean_res = None
		if len(splitted_value) > 1:
			replace_spaces = value.replace(' ', '+')
		else:
			clean_res = value
		return clean_res

	def _print_head(self, word):
		asteriks = '*' * 5
		head = asteriks + f' [{word.capitalize()}] ' + asteriks
		print(head)

	def _detect_final_api(self, **params) -> str:
		starts_with = None
		max_ = None
		main_param = None
		for param, value in params.items():
			if param == 'starts_with':
				starts_with:str = value
			elif param == 'main_param':
				main_param:str = value
			else:
				max_:int = value

		api = None
		if not starts_with and not max_:
			mp, wc = main_param, self._word_for_api
			api = f'https://api.datamuse.com/words?{mp}={wc}'
		elif starts_with and not max_:
			params_set:tuple = (main_param, self._word_for_api, starts_with)
			api = 'https://api.datamuse.com/' \
				  'words?%s=%s&sp=%s*' % params_set
		elif not starts_with and max_:
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&max=%d' % (main_param, self._word_for_api, max_)
		else:
			params_set:tuple = (main_param, self._word_for_api,
				                starts_with, max_)
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&sp=%s*&max=%d' % params_set
		return api

	def _get_json(self, api: str):
		response = requests.get(api)
		json_data = json.loads(response.text)

		return json_data

	def _prevent_repetition(self, data: list) -> list:
		for num_of_iter, dict_ in enumerate(data):
			if dict_['word'] == self.word:
				data.pop(num_of_iter)
			else:
				continue
		return data

	# REST API
	def get_usage(self, display=False) -> list:
		apiurl = 'https://lt-collocation-test.herokuapp.com/todos/'\
		         '?query=%s&lang=en' % self._word_for_api

		json_data = self._get_json(apiurl)

		examples:list = []
		for i in json_data:
			ex = i['examples']
			for e in ex:
				if isinstance(e, str):
					clean_line = re.sub(self.HTML_TAGS, '', e)
					examples.append(clean_line)
		
		if display:
			self._print_head(self.word)
			for num, ex in enumerate(examples):
				print(f'{num + 1}) {ex}')
		return examples

	def predict_gender_if_name(self, display=False) -> dict:
		api = f'https://api.genderize.io/?name={self.word}'
		get_json:dict = self._get_json(api)
		name = self.word.capitalize()
		get_json['name'] = name

		if display:
			self._print_head(name)
			probability_raw = round(get_json['probability'] * 100, 2)
			prob = str(probability_raw) + ' %'
			msg = "Gender: %s\nProbability: %s" % (get_json['gender'], prob)
			print(msg)
			print('_' * len(head))

		return get_json

	async def predict_nationality_if_name(self, display=False) -> dict:
		api = f'https://api.nationalize.io/?name={self.word}'
		return api
		get_json:dict = self._get_json(api)
		name = self.word.capitalize()
		get_json['name'] = name

		if display:
			self._print_head(name)

			country = get_json['country']
			for c in country:
				print(f"Country id: {c['country_id']}")
				probability_raw = round(c['probability'] * 100, 2)
				probability = str(probability_raw) + ' %'
				print(f'Probability: {probability}')
				print('_' * len(head))
		return get_json

	def get_similar_meanings(self, starts_with=None, max_=None,
		                     display=False) -> list:

		kwargs_for_method:dict = {
			'starts_with': starts_with,
			'max_': max_,
			'main_param': 'ml'
		}
		api = self._detect_final_api(**kwargs_for_method)
		data: list = self._get_json(api)

		if display:
			self._print_head(self.word)
			for num, dict_ in enumerate(data):
				msg_raw = '%d) %s,' % (num, dict_['word'].capitalize())
				tags = f" tags: {dict_['tags']}"
				msg_clean = msg_raw + tags
				print(msg_clean)
		return data

	def get_words_that_sound_like(self, starts_with=None, max_=None,
		                          display=False) -> list:
		"""Get words that sound like self.word"""

		kwargs_for_method:dict = {
			'starts_with': starts_with,
			'max_': max_,
			'main_param': 'sl'
		}

		api = self._detect_final_api(**kwargs_for_method)
		data: list = self._get_json(api)

		if display:
			self._print_head(self.word)

			for num, dict_ in enumerate(data):
				msg_raw = '%d) %s,' % (num + 1, dict_['word'].capitalize())
				num_of_sylables = f" num of sylables: {dict_['numSyllables']}"
				msg_clean = msg_raw + num_of_sylables
				print(msg_clean)
		return data

	def get_words_that_spelled_similarly(self, max_=None, 
		                                 display=False) -> list:

		kwargs_for_method:dict = {
			'max_': max_,
			'main_param': 'sp'
		}

		api = self._detect_final_api(**kwargs_for_method)
		data: list = self._get_json(api)

		clean_data: list = self._prevent_repetition(data)

		if display:
			self._print_head(self.word)
			for num, dict_ in enumerate(clean_data):
				msg = '%d) %s' % (num + 1, dict_['word'].capitalize())
				print(msg)
		return clean_data

	async def get_words_that_rhyme_with(self, starts_with=None, max_=None,
	                              display=False) -> list:
		kwargs_for_method:dict = {
			'starts_with': starts_with,
			'max_': max_,
			'main_param': 'rel_rhy'
		}

		new_api: list = []
		api = self._detect_final_api(**kwargs_for_method)
		return api
		# data: list = 
		return data

		clean_data: list = self._prevent_repetition(data)

		if display:
			self._print_head(self.word)
			for num, dict_ in enumerate(clean_data):
				msg = '%d) %s' % (num + 1, dict_['word'].capitalize())
				print(msg)
		return clean_data

	async def task_async(self, *funcs):
		urls = []
		for func in funcs:
			res = await func(self)
			urls.append(res)
		res = await async_HTTP_request(urls)
		return res
		

word = Word('hello')
loop = asyncio.get_event_loop()
urls = (Word.predict_nationality_if_name, Word.predict_nationality_if_name,
Word.predict_nationality_if_name)
task = word.task_async(*urls)
res = loop.run_until_complete(task)
pprint.pprint(res)