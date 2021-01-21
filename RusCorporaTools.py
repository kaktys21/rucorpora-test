import os
import re
import csv
import time
import random
import requests
import datetime
from itertools import chain
from bs4 import BeautifulSoup

'''Работа с нкря'''

'''Starting preparations'''
dir_list = os.listdir()
must_dir = ['CorporaFail', 'CorporaSentences', 'testOut']
for directory in must_dir:
	if directory not in dir_list:
		os.mkdir(directory)

class GetFunc:

	'''Only function class
	Functions with requests'''

	@staticmethod
	def html(link):
	      
		'''HTML getter'''

		#time.sleep(1) # В целом, это можно убрать, но иногда ругается
		return requests.get(link).text

	@staticmethod
	def next_page(link):
		
		'''
		Next page link getter
		It can be writter much faster, but this algo gives 100% correct link
		'''
		
		soup = BeautifulSoup(GetFunc.html(link), features="lxml")
		next_page_text = soup.find('p', {'class': 'pager'}).find_all('a')[-1:][0].text
		if next_page_text == "следующая страница":
			res = re.match(r'http(.)+search', link)
			next_page = res.group(0)[:-6] + soup.find('p', {'class': 'pager'}).find_all('a')[-1:][0].get('href')
			return next_page
		else:
			return 'end'

	@staticmethod
	def fast_pager(link):
		return int(int(BeautifulSoup(GetFunc.html(link), features='lxml').find_all('span', {'class': 'stat-number'})[-2].text) / 10)
	
	@staticmethod
	def tables(link):
		
		'''Gets tables from html with sentences/word speqs'''
		
		tables = BeautifulSoup(GetFunc.html(link), features = "lxml").find_all('table')
		if len(tables) == 0:
			print('Server blocking, please wait')
			time.sleep(5)
			GetFunc.tables(link)
		else:
			return tables

	@staticmethod
	def search_word_dict(link, sent):
		
		'''Creates a link dict to get word speqs'''

		if sent == None: 
			return None
		time.sleep(4)       
		sent = '+'.join(sent.split())
		link = re.sub(r'&p=[1-9]+', '', link)
		new_link = re.sub(r'req=(.)*&mycorp', 'req=' + sent + '&mycorp', link)
		try:
			tables = GetFunc.tables(new_link)[2]
			tr_list = tables.find_all('span')[:-2]
			res = dict()
			for span in tr_list:
				res[span.text] = CreatFunc.info_link_creator(new_link, span.get('explain'))
				return res
		except:
			return None	

	@staticmethod
	def speq(words: dict, test=False):
		
		'''
		From words dict returns a list of tuples
		(word, speq dict)
		if a word has different speq sets, returns numbered word
		for each set of speqs
		'''
		
		res = []
		for word in words:
			if test == True:
				print(word)
			i = 1
			time.sleep(1)
			table = GetFunc.tables(words[word])[0]
			curent_dict = dict()
			tr_list = table.find_all('tr')[1:]
			word = table.find('tr').text
			for tr_num in range(len(tr_list)):
				td_list = tr_list[tr_num].find_all('td')
				if td_list[0].text in curent_dict:
					res.append((word + str(i), curent_dict))
					curent_dict = {td_list[0].text:td_list[1].text}
					i += 1
				else:
					curent_dict[td_list[0].text] = td_list[1].text
			res.append((word + str(i), curent_dict) if i != 1 else (word, curent_dict))
		return res

	@staticmethod
	def text(link, page=1, trash_out=r'CorporaFail\Failed.txt'):
		
		'''
		Returns a list of sentences with word speq links dicts
		This function do not return speqs, because corpora cannot wqork with 
		many requests/second and blocks
		'''
		
		print(f'Page loading - {page}')
		tables = GetFunc.tables(link)[2:-2]
		final_res = []
		for r_num in range(len(tables)):
			table_text = tables[r_num].text
			sentences = table_text.split('←…→')[:-1]
			sent_len = len(sentences)
			flag = 1 if sent_len > 1 else 0
			if flag == 1:
				print(f'{sent_len * 4} second sleep not to break the RusCorpora syte')
			for sentence in sentences:
				res = [s.strip(' []') for s in sentence.strip(' ').split('[')]
				if flag == 0:
					tr_list = tables[r_num].find_all('span')[:-2]
					sub_res = dict()
					for span in tr_list:
						explain = span.get('explain')
						sub_res[span.text] = CreatFunc.info_link_creator(link, span.get('explain'))
					res.append(sub_res)
				else:      
					res.append(GetFunc.search_word_dict(link, res[0] if len(res) == 3 else None))
				if len(res) == 4 and res[3] != None:
					final_res.append(res)
				else:
					with open(trash_out, 'w', encoding='utf-8') as f:
						f.write(' '.join(res[:-1]))
		return final_res

	@staticmethod
	def page_num_fast_taker(link):
		docs = int(BeautifulSoup(GetFunc.html(link), features='lxml').find_all('span', {'class': 'stat-number'})[-2].text)
		return docs // 10 + (1 if docs % 10 != 0 else 0)

class CreatFunc:

	'''Class only for tecnical functions without requests'''
	
	@staticmethod
	def info_link_creator(link, explain):
		
		'''Word speq link creator'''
		
		return re.sub(r'&text=lexform', '', link) + '&text=word-info&requestid=' + str(random.randint(0, 10 ** 13)) + '&language=ru&source=' + explain
	
	@staticmethod
	def word_dict(link, table):
		
		'''From link and sentence creates a speq links dict'''
		
		trlist = table.find_all('span')[:-2]
		sub_res = dict()
		for span in trlist:
			explain = span.get('explain')
			sub_res[span.text] = CreatFunc.info_link_creator(link, span.get('explain'))
		return sub_res

	@staticmethod
	def tables_with_html(html):
		
		'''Gets tables from html with sentences/word speqs'''
		
		tables = BeautifulSoup(html, features="lxml").find_all('table')
		if len(tables) == 0:
			print('Server blocking, please wait')
			time.sleep(5)
			CreatFunc.tables_with_html(link)
		else:
			return tables		 
	
class CsSentences:
	
	'''Sentence class'''
	
	def __init__(self, link, file_name=r'CorporaSentences\OutPut', test=False):
		
		'''
		Returns a search result formed in list (sentence, source, omonimia)
		failed ones (if corpora has some mistakes in formatting) go to Failed.txt
		in the folder CorporaFail
		'''

		self.link = link
		self.__file = file_name

		if 'CorporaFail' not in os.listdir():
			os.mkdir('CorporaFail')
		trash_out = r'CorporaFail\Failed.txt'
		page = 1
		self.full_sent = []
		
		while True:
			if link == 'end':
				break
			self.full_sent += GetFunc.text(link, page, trash_out)
			page += 1
			link = GetFunc.next_page(link)

		if test == True:
			print('Done')
			
		return self.full_sent
	
	def to_file(self):

		'''
		Saves the search result to a OutPut.csv file in the folder CorporaSentences
		There can be problems with opening this file with excel
		So, use notepad or try this to make right encoding:
		    1) Data
		    2) From text/CSV file...
		    3) Set utf-8 encoding
		    4) Give yourself a choco because you are breathakinkg
		'''
		       
		self.__file = self.__file[:-4] if self.__file.endswith('.txt') else self.__file
		with open(self.__file + '.csv', 'w', encoding = 'utf-8') as out:
			out_file = csv.writer(out, delimiter = ';', lineterminator = '\r')
			out_file.writerow(['Предложение', 'Источник', 'Омонимия'])     
			for r in self.full_sent:
				for re in r:
					out_file.writerow(re[:-1])	
					
	def get_sentences(self):
		
		'''Returns only sentences'''
		
		return list(sentence[0] for sentence in self.full_sent)
		
	def omonim_on(self):
		
		'''Returns sentences without omonimia'''
		
		return list(sentence[0] for sentence in self.full_sent if sentence[2] == 'омонимия снята')
	
	def omonim_off(self):
		
		'''Returns sentences with omonimia'''

		return list(sentence[0] for sentence in self.full_sent if sentence[2] == 'омонимия не снята')

	@staticmethod
	def get_sent_num(self, sent):
		
		'''Returns sentence number by sentence'''
		
		for i in range(len(self.full_sent)):
			if self.full_sent[i][0] == sent:
				return i + 1
		
	
	def sent_word_speq(self, sent):
		
		'''
		Returns word speqs by sentence
		The longer the sentence the longer works not to break RusCorpora syte
		'''
		
		sent_num = CsSentences.get_sent_num(self, sent)
		sent = self.full_sent[sent_num - 1]
		print(f'{len(sent[0].split())} second sleep not to break RusCorpora syte')
		return GetFunc.speq(sent[3])
	
class CorporaInfo:
	
	'''
	Quantity corpora info
	Works with a "*" search result link
	'''
	
	def __init__(self, link, file_name = r'CorporaSentences\OutPut'):
		
		self.link = link
		self.filename = file_name
		#self.lexem_dict = '''Словарь лексем - лексема:кол-во вхождений'''

	def lexem_dict(self, test=False):
		
		'''
		Lexem dict - lexem:number in corpora
		'''
		s = time.time()
		link = self.link
		name_by_value = dict()
		pager = 1
		test_time = []
		print(f'It takes around 8 seconds to parse one page, so...\n You have {datetime.timedelta(seconds=GetFunc.page_num_fast_taker(link) * 8)}\nMake some tea, find coockies and wait =)\n')
		while True:
			if test == True:
				start_time = time.time()
				print(pager)
			if link == 'end':
				
				if test == True:
					for i in range(len(test_time)):
						print(f'Page {i + 1} - {test_time[i]}')
					print(sum(test_time) / len(test_time))

				return name_by_value
			
			html = GetFunc.html(link)
			tables = CreatFunc.tables_with_html(html)[-2:][0]
			for tr in tables.select('tr'):
				tds = tr.select('td')
				if len(tds) < 3:
					pass
				else:
					name, value = tds[1].text.strip(), int(tds[2].text.strip())
					if name not in name_by_value:
						name_by_value[name] = value
					else:
						name_by_value[name] += value
			pager += 1
			link = GetFunc.next_page(link)
			if test == True:
				s = time.time() - start_time
				test_time.append(s)
				print(s)
			
		return name_by_value