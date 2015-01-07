#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import urllib2
import threading
from bs4 import BeautifulSoup

def getPage(url, timeout):
	try:
		req = urllib2.Request(url)
		resp = urllib2.urlopen(req, timeout=timeout)
		data = resp.read()
		resp.close()
		return data
	except Exception, e:
		print e

def savePage(path, title, url, retry):
	while retry >= 0:
		print 'downloading ' + title + '...'
		page = getPage(url, 10)
		if page is not None:
			file = open(path + '/' + title + '.html','w')
			file.write(page)
			file.close()
			print title + ' Finished!'
			break;
		else:
			print title + ' Failed!'
			retry = retry - 1
			if retry >= 0:
				print 'try again...'

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		print 'no url input!'
	else:
		# such as http://chimera.labs.oreilly.com/books/1230000000545/index.html
		url_prefix = re.sub(r'index\.html', '', sys.argv[1])
		print 'Extracting contents...'
		data = getPage(url_prefix + 'index.html',10)
		if data is not None:
			p = re.compile(r'[^\w\- ]')
			soup = BeautifulSoup(data)
			book = p.sub('',soup.html.head.title.contents[0])
			if not os.path.exists(book):
				os.mkdir(book)
			print book
			span = soup.findAll('span',{'class' : ['chapter', 'preface']})
			for link in span:
				title = p.sub('',link.a.contents[0])
				turl = url_prefix + link.a['href']
				threading.Thread(target=savePage, args=(book, title, turl, 1)).start()

