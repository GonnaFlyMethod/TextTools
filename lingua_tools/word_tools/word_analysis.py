import re
import itertools
import requests
import json
import pprint
import asyncio
from typing import Union
from aiohttp import ClientSession
from _async import async_HTTP_request
import time

class Word():

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

	def _print_head(self, word, type_of_analysis):
		asteriks = '*' * 5
		t_of_analysis: str = f'| Type of analysis: {type_of_analysis.lower()}'
		head = asteriks + f' [{word.capitalize()} {t_of_analysis}] ' + asteriks
		print(head)

	def _detect_final_api(self, **params) -> str:
		starts_with = None
		max_ = None
		main_param = None
		additional_param = None
		additional_param_value = None
		for param, value in params.items():
			if param == 'starts_with':
				starts_with:str = value
			elif param == 'main_param':
				main_param:str = value
			elif param == 'max_':
				max_:int = value

			# Other information
			else:
				additional_param: str = value['additional_param']
				additional_param_value: str = value['value']

		api = None

		if (not starts_with and main_param != 'sug?s' and not max_
		   and not additional_param):
			mp, wc = main_param, self._word_for_api
			api = f'https://api.datamuse.com/words?{mp}={wc}'
		elif (starts_with and main_param != 'sug?s' and not max_
		      and not additional_param):
			params_set:tuple = (main_param, self._word_for_api, starts_with)
			api = 'https://api.datamuse.com/' \
				  'words?%s=%s&sp=%s*' % params_set
		elif (not starts_with and main_param != 'sug?s' and max_
		     and not additional_param):
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&max=%d' % (main_param, self._word_for_api, max_)
		elif (starts_with and main_param != 'sug?s' and max_
		     and not additional_param):
			params_set:tuple = (main_param, self._word_for_api,
				                starts_with, max_)
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&sp=%s*&max=%d' % params_set
		elif (not starts_with and main_param != 'sug?s' and not max_
		     and additional_param):
			params_set:tuple = (main_param, self._word_for_api,
				                additional_param, additional_param_value)
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&%s=%s' % params_set
		elif (starts_with and main_param != 'sug?s' and not max_
		     and additional_param):
			params_set:tuple = (main_param, self._word_for_api, starts_with,
								additional_param, additional_param_value)
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&sp=%s*&%s=%s' % params_set
		elif main_param == 'sug?s' and not max_:
			params_set:tuple = (main_param, self._word_for_api)
			api = 'https://api.datamuse.com/%s=%s' % params_set
		elif main_param == 'sug?s' and max_:
			params_set:tuple = (main_param, self._word_for_api, max_)				          
			api = 'https://api.datamuse.com/%s=%s&max=%d' % params_set
		else:
			params_set:tuple = (main_param, self._word_for_api, starts_with,
								max_, additional_param, additional_param_value)
			api = 'https://api.datamuse.com/' \
			      'words?%s=%s&sp=%s*&max=%d&%s=%s' % params_set
		return api

	def _prevent_repetition(self, data: list) -> list:
		for num_of_iter, dict_ in enumerate(data):
			if dict_['word'] == self.word:
				data.pop(num_of_iter)
			else:
				continue
		return data

	# REST API
	async def get_usage(self, display=False, data=False) -> Union[str, None]:

		if not display and not data:
			api = 'https://lt-collocation-test.herokuapp.com/todos/'\
				  '?query=%s&lang=en' % self._word_for_api
			return api
		else:
			examples:list = []
			for i in data:
				ex = i['examples']
				for e in ex:
					if isinstance(e, str):
						html_tags_killer_re = r'<\/?\w+(\s+)?[^>]*>'
						clean_line = re.sub(html_tags_killer_re, '', e)
						examples.append(clean_line)
			self._print_head(self.word, 'Usage')
			for num, ex in enumerate(examples):
				print(f'{num + 1}) {ex}')
			print('_' * 60)

	async def predict_gender_if_name(self, display=False,
		                             data=False) -> Union[str, None]:

		if not display and not data:
			api = f'https://api.genderize.io/?name={self.word}'
			return api

		else:
			self._print_head(self.word, 'prediction of gender by name')
			probability_raw = round(data['probability'] * 100, 2)
			prob = str(probability_raw) + ' %'
			msg = "Gender: %s\nProbability: %s" % (data['gender'], prob)
			print(msg)
			print('_' * 60)

	async def predict_nationality_if_name(self, display=False,
		                                  data=False) -> Union[str, None]:
		if not display and not data:
			api = f'https://api.nationalize.io/?name={self.word}'
			return api
		else:
			self._print_head(self.word, 'prediction of nationality by name')

			country = data['country']
			for c in country:
				print(f"Country id: {c['country_id']}")
				probability_raw = round(c['probability'] * 100, 2)
				probability = str(probability_raw) + ' %'
				print(f'Probability: {probability}')
			print('_' * 60)

	async def get_similar_meanings(self, starts_with=None, max_=None,
		                           display=False,
		                           data=False) -> Union[str, None]:

		if not display and not data:
			kwargs_for_method:dict = {
				'starts_with': starts_with,
				'max_': max_,
				'main_param': 'ml'
			}
			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			type_ = f'words that have similar meanings with {self.word}'
			self._print_head(self.word, type_)
			for num, dict_ in enumerate(data):
				msg_raw = '%d) %s,' % (num + 1, dict_['word'].capitalize())

				tags = ''
				try:
					tags = f" tags: {dict_['tags']}"
				except KeyError:
					pass

				msg_clean = msg_raw + tags
				print(msg_clean)
			print('_' * 60)

	async def get_words_that_sound_like(self, starts_with=None, max_=None,
										display=False,
		                                data=False) -> Union[str, None]:
		"""Get words that sound like self.word"""

		if not display and not data:
			kwargs_for_method:dict = {
				'starts_with': starts_with,
				'max_': max_,
				'main_param': 'sl',
			}

			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			type_ = f'words that sound like {self.word}'
			self._print_head(self.word, type_)

			for num, dict_ in enumerate(data):
				msg_raw = '%d) %s,' % (num + 1, dict_['word'].capitalize())
				num_of_sylables = f" num of sylables: {dict_['numSyllables']}"
				msg_clean = msg_raw + num_of_sylables
				print(msg_clean)
			print('_' * 60)

	async def get_words_that_spelled_similarly(self, max_=None, display=False,
		                                       data=False) -> Union[str, None]:

		if not display and not data:
			kwargs_for_method:dict = {
				'max_': max_,
				'main_param': 'sp'
			}
			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			clean_data: list = self._prevent_repetition(data)
			type_ = f'words that spelled similarly with {self.word}'
			self._print_head(self.word, type_)
			for num, dict_ in enumerate(clean_data):
				msg = '%d) %s' % (num + 1, dict_['word'].capitalize())
				print(msg)
			print('_' * 60)

	async def get_words_that_rhyme_with(self, starts_with=None, max_=None,
	                                    display=False, related_to=None,
	                                    data=None) -> Union[str, None]:

		if not display and not data:
			kwargs_for_method:dict = {
				'starts_with': starts_with,
				'max_': max_,
				'main_param': 'rel_rhy',
				'other': {'additional_param':'ml', 'value': related_to}
			}

			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			clean_data: list = self._prevent_repetition(data)
			type_ = f'words that rhyme with {self.word}'
			self._print_head(self.word, type_)
			for num, dict_ in enumerate(clean_data):
				msg = '%d) %s' % (num + 1, dict_['word'].capitalize())
				print(msg)
			print('_' * 60)

	async def get_words_that_related(self, starts_with=None, max_=None,
		                                  display=None, topics=None,
		                                  data=None) -> Union[str, None]:
		if not display and not data:
			kwargs_for_method:dict = {
				'starts_with': starts_with,
				'max_': max_,
				'main_param': 'rel_jjb',
				'other': {'additional_param':'topics', 'value': topics}
			}

			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			type_ = f'related words for {self.word}'
			self._print_head(self.word, type_)
			for num, dict_ in enumerate(data):
				word_for_print: str = dict_['word'].capitalize()
				msg = '%d) %s, ' \
					  'score: %d' % (num + 1, word_for_print, dict_['score'])
				print(msg)
			print('_' * 60)

	async def get_suggestions(self, max_=None, display=False,
		                      data=None) -> Union[str, None]:
		if not display and not data:
			kwargs_for_method:dict = {
				'max_': max_,
				'main_param': 'sug?s',
			}

			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			type_ = f'suggestions for {self.word}'
			self._print_head(self.word, type_)
			for num, dict_ in enumerate(data):
				word_for_print: str = dict_['word'].capitalize()
				msg = '%d) %s, ' \
					  'score: %d' % (num + 1, word_for_print, dict_['score'])
				print(msg)
			print('_' * 60)

	async def get_nouns_that_described_by_the_word(self, max_=None,
		                                         display=False,
		                                         data=None) -> Union[str, None]:

		if not display and not data:
			kwargs_for_method:dict = {
				'max_': max_,
				'main_param': 'rel_jja',
			}

			api = self._detect_final_api(**kwargs_for_method)
			return api
		else:
			type_ = f'nouns that are often described by word {self.word}'
			self._print_head(self.word, type_)
			for num, dict_ in enumerate(data):
				word_for_print: str = dict_['word'].capitalize()
				msg = '%d) %s, ' \
					  'score: %d' % (num + 1, word_for_print, dict_['score'])
				print(msg)
			print('_' * 60)

	async def task_async(self, *funcs_and_kwargs, display=False) -> dict:
		urls = []
		functions_name_and_functions_objs:dict = {}
		functions_name_and_urls: dict = {}
		res = None
		for func, kwargs in funcs_and_args:

			if not kwargs:
				res = await func(self)
			else:
				res = await func(self, **kwargs)
			functions_name_and_urls[func.__name__] = res
			functions_name_and_functions_objs[func.__name__] = func
		res:list = await async_HTTP_request(functions_name_and_urls)

		final_res: dict = {}
		for dict_ in res:
			final_res.update(dict_)

		if display:
			for func, res in final_res.items():
				func_obj = functions_name_and_functions_objs[func]
				await func_obj(self, display=True, data=res)
		return final_res

word = Word('Body')
loop = asyncio.get_event_loop()

funcs_and_args = [
				  (Word.get_words_that_related, {'starts_with': 'F', 'max_':2, 
				  	                             'topics':'health'}),
				  (Word.get_usage, None),
				  (Word.get_words_that_sound_like, None),
				  (Word.get_suggestions, {'max_':6}),
				  (Word.get_nouns_that_described_by_the_word, None)
				  ]

task = word.task_async(*funcs_and_args, display=True)
res = loop.run_until_complete(task)
