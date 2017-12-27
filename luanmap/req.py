# -*- coding:utf-8 -*-
import requests,cPickle
SUCESS = 'U*'
class Request_data:
	def readFile(self,path):
		f = open(path,'r')
		self.data = cPickle.load(f)
		self.submit = cPickle.load(f)
		self.sqli_payload = cPickle.load(f)
		f.close()
	def writeFile(self,path):
		f = open(path,'w')
		cPickle.dump(self.data, f)
		cPickle.dump(self.submit, f)
		cPickle.dump(self.sqli_payload, f)
		f.close()
	def findValueByKey(self,key):
		if key in self.data['get_dic']:
			return self.data['get_dic'][key]
		elif key in self.data['post_dic']:
			return self.data['post_dic'][key]
		elif key in self.data['headers']:
			return self.data['headers'][key]
	def get_InjectParameter(self):
		for getname in self.data['get_dic']:
			if '#InjectHere#' in self.data['get_dic'][getname]:
				return ''.join([getname,' (GET)'])
		for postname in self.data['post_dic']:
			if '#InjectHere#' in self.data['post_dic'][postname]:
				return ''.join([postname,' (POST)'])
		for header in self.data['headers']:
			if '#InjectHere#' in self.data['headers'][header]:
				return ''.join([header,' (HEADER)'])
	def have_InjectHere(self):
		return '#InjectHere#' in ' '.join([self.data['url'],self.data['postdata'],str(self.data['headers'])])
	def __cmp__(self,other):
		return self.data == other.data
	def replace(self,dest,src,key=''):
		if key == '':
			for getname in self.data['get_dic']:
				self.data['get_dic'][getname] = self.data['get_dic'][getname].replace(dest,src)
			self.data['url'] = '?'.join([self.data['url'].split('?')[0],'&'.join(map(lambda x:'='.join(x),self.data['get_dic'].items()))])
			for postname in self.data['post_dic']:
				self.data['post_dic'][postname] = self.data['post_dic'][postname].replace(dest,src)
			self.data['postdata'] = '&'.join(map(lambda x:'='.join(x),self.data['post_dic'].items()))
			for header in self.data['headers']:
				self.data['headers'][header] = self.data['headers'][header].replace(dest,src)
		else:
			try:
				self.data['get_dic'][key] = self.data['get_dic'][key].replace(dest,src)
				self.data['url'] = '?'.join([self.data['url'].split('?')[0],'&'.join(map(lambda x:'='.join(x),self.data['get_dic'].items()))])
			except KeyError:
				pass	
			try:
				self.data['post_dic'][key] = self.data['post_dic'][key].replace(dest,src)
				self.data['postdata'] = '&'.join(map(lambda x:'='.join(x),self.data['post_dic'].items()))
			except KeyError:
				pass
			try:
				self.data['headers'][key] = self.data['headers'][key].replace(dest,src)
			except KeyError:
				pass
	def send(self,timeout=5):
		'''
		if self.have_replace == False:
			self.have_replace = True
			self.replace_list(self.special_keywords,self.bypass_keywords)
		'''
		proxies = {
			"http": self.proxy,
			"https": self.proxy
			}
		timeout_count = 0
		while timeout_count != 2:
			try:
				if self.submit == 'auto':
					if self.data['postdata'] == '':
						return requests.get(url=self.data['url'],data=self.data['post_dic'],headers=self.data['headers'],proxies=proxies,timeout=timeout, verify=False).content
					else:
						return requests.post(url=self.data['url'],data=self.data['post_dic'],headers=self.data['headers'],proxies=proxies,timeout=timeout, verify=False).content
				elif self.submit == 'get':
					return requests.get(url=self.data['url'],data=self.data['post_dic'],headers=self.data['headers'],proxies=proxies,timeout=timeout, verify=False).content
				elif self.submit == 'post':
					return requests.post(url=self.data['url'],data=self.data['post_dic'],headers=self.data['headers'],proxies=proxies,timeout=timeout, verify=False).content
				else:
					raise ValueError,"".join(self.submit," method is not support")
			except Exception:
				if timeout != 5:
					raise
				timeout_count += 1
				print 'timeout,try again'
	def replace_list(self,special_keywords=[],bypass_keywords=[]):
		for index,special_keyword in enumerate(special_keywords):
			self.replace(special_keyword,bypass_keywords[index])
	def __init__(self,req_data,submit = 'auto',special_keywords=[],bypass_keywords=[]):
		self.time_sec = 1
		self.special_keywords = special_keywords
		self.bypass_keywords = bypass_keywords
		self.have_replace = False
		self.submit = submit.lower()
		self.data = req_data
		self.sqli_payload = ''
		self.proxy = ''
		self.trueCode = ''
		self.timeout_count = 2
		if len(self.data['url'].split('?')) != 1:
			getdata = self.data['url'].split('?')[1].split('&')
			for paramer in getdata:
				paramers = paramer.split('=')
				key = paramers[0]
				paramers.remove(key)
				self.data['get_dic'][key] = '='.join(paramers)
		if self.data['postdata'] != "":
			postdata = self.data['postdata'].split('&')
			for paramer in postdata:
				paramers = paramer.split('=')
				key = paramers[0]
				paramers.remove(key)
				self.data['post_dic'][key] = '='.join(paramers)
	def get_sqli_payload(self):
		return self.sqli_payload