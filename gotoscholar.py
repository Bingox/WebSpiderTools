#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import random
import hashlib
import urllib2
import threading
from bs4 import BeautifulSoup
from htmlentitydefs import name2codepoint

# fake google id (looks like it is a 16 elements hex)
rand_str = str(random.random()).encode('utf8')
google_id = hashlib.md5(rand_str).hexdigest()[:16]

GOOGLE_SCHOLAR_URL = "http://scholar.google.com"
# the cookie looks normally like:
#        'Cookie' : 'GSP=ID=%s:CF=4' % google_id }
# where CF is the format (e.g. bibtex). since we don't know the format yet, we
# have to append it later
HEADERS = {'User-Agent': 'Mozilla/5.0',
           'Cookie': 'GSP=ID=%s' % google_id}

BIBTEX = 4
ENDNOTE = 3
REFMAN = 2
WENXIANWANG = 5

def search(url, headers):
	req = urllib2.Request(url, headers = headers)
	resp = urllib2.urlopen(req)
	data = resp.read().decode('utf8')
	resp.close()
	return data

def printCitations(url, headers):
	global citations
	data = search(url, headers)
	if mutex.acquire():
		citations.append(data)
		mutex.release()
		print threading.currentThread().getName()

def getCitations(query, outformat=BIBTEX):
	try:
		url = 'http://scholar.google.com/scholar?q=' + urllib2.quote(query)
		headers = HEADERS
		headers['Cookie'] = headers['Cookie'] + ":CF=%d" % outformat
		print 'requesting...'
		data = search(url, headers)
		links = getLinks(data, outformat)
		threadList = []
		for link in links:
			url = 'http://scholar.google.com' + link
			t = threading.Thread(target=printCitations, args=(url, headers))
			threadList.append(t)
			t.start()
		for thread in threadList:
			thread.join()
			print thread.getName() + ' Finished'
		print 'All Finished!'
	except Exception, e:
		print e

def getLinks(data, outformat):
	if outformat == BIBTEX:
		rc = re.compile(r'<a href="(/scholar\.bib\?[^"]*)')
	elif outformat == ENDNOTE:
		rc = re.compile(r'<a href="(/scholar\.enw\?[^"]*)"')
	elif outformat == REFMAN:
		rc = re.compile(r'<a href="(/scholar\.ris\?[^"]*)"')
	elif outformat == WENXIANWANG:
		rc = re.compile(r'<a href="(/scholar\.ral\?[^"]*)"')
	hrefs = rc.findall(data)
	links = [re.sub('&(%s);' % '|'.join(name2codepoint), lambda m : chr(name2codepoint[m.group(1)]), s) for s in hrefs]
	return links

citations = []
mutex = threading.Lock()

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		print 'no input!'
	else:
		proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
		query = re.sub(r'\ +','+',sys.argv[1].strip())
		getCitations(query)
		query = re.sub(r'[^\w\- ]',' ',query)
		file = open(query + '.bib','w')
		citations = '\n'.join(citations)
		file.write(citations)
		file.close()
		print 'Write to file.'
		

