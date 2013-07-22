#!/usr/bin/env python
import mechanize
import cookielib
import re
import os
import sys
import signal
import atexit
import pickle
import time
from BeautifulSoup import BeautifulSoup as bs

#import dblib

state = []
re_sort = re.compile(r"\d*(?=\.html)")
re_uid = re.compile(r"\d*$")
i_page = None
i_thread = None
i_tpage = None
i = None

def _init_browser():
	global br
#con, cur = dblib.setup_db()

	br = mechanize.Browser()
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

# Browser options
	br.set_handle_equiv(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0')]
	"""
	try:
	cj.load("cookie123")
	print "Cookie loaded"
	except:
	"""
#Login
	print "(Cookie not found. Logging in!)"
	r = br.open('http://www.hackforums.net/showthread.php?tid=3639226')
	br.select_form(nr=0)
	br["username"] = "cant_buy_me_love"
	br["password"] = "aZerba1Jan"
	results = br.submit().read()
	cj.save("cookie123")
	return br

def request_page(page):
	global br
	tries = 0
	while tries < 10:
		try:
			r = br.open(page)
			return r
		except Exception as e:
			print "Error: %s" % e.code
			tries+=1
			time.sleep(10)
	print "Fatal error. Restarting browser."
	br = _init_browser()
	sys.exit(0)	

def interrupt(signal, frame):
	sys.exit(0)

def _save_state():
	global br
	br.close()
	f = open(".hackforums.p", "w")
	print "EXITING. SAVING STATE TO FILE."
	state[3] = i_page
	state[4] = i_thread
	state[5] = i_tpage
	pickle.dump(state, f)
	f.close()
	print "subforum page = %s\n\
	thread # = %s\n\
	thread page # = %s" % (state[3], state[4], state[5])

def get_links():
	"""
	get_links()
	input: mechanize browser object
	gets all thread links and page links from myBB style forum archive page
	returns: (page_links, thread_links)
	where each thread_link is a tuple of (url, title)
	"""
	global br

	raw_urls = []
	for link in br.links():
		raw_urls.append(link)

	assert raw_urls

	plx = []
	tlx = []
	for link in raw_urls:
		if link.attrs:
			url = link.attrs[0][1]
			if re.search(r"/archive/index\.php/forum-114-", url):
				plx.append(url)
			if re.search(r"/archive/index\.php/thread-", url):
				tlx.append((url, link.text))
	plx = sorted(list(set(plx)), key=lambda x: int(re_sort.findall(x)[0]))
	return plx, tlx

atexit.register(_save_state)

try:
	f = open(".hackforums.p", "rw")
	state = pickle.load(f)
except:
	state = [None]*6
	print "No save file found. Initiating new scrape."

if len(sys.argv) < 3:
	print "Usage: python hackdump.py dir link"

br = _init_browser()

homedir = sys.argv[1]
sublink = sys.argv[2]

#homedir = "hackdumps/"
#sublink = "http://www.hackforums.net/archive/index.php/forum-114.html"
r = request_page(sublink)
cur_page = br.geturl()

page_links, thread_links = get_links()

if not os.path.exists(homedir):
	os.makedirs(homedir)

if state[0] is None:
#if page_link is not yet defined
	state[0] = page_links
	state[1] = thread_links
	print "Initiating new scrape."
else:
	page_links = state[0]
	thread_links = state[1]
	print "Resuming scrape."


if state[3] is not None:
	#i_page
	i_page = state[3]
	print "Resuming scrape on subforum page %d" % i_page
else:
	i_page = -1
	state[3] = i_page

while i_page < len(page_links):
	sdir = homedir + str(i_page+2) + "/"
	if not os.path.exists(sdir):
		os.makedirs(sdir)
	if i_page == state[3] and state[4] is not None: #state[4] is i_thread
		thread_links = state[1]
		i_thread = state[4]
		print "Resuming scrape on thread %d" % i_thread
	else:
		i_thread = 0
		state[4] = i_thread
	if i_page!=-1: #skip first time
		r = request_page(page_links[i_page])
		thread_links = get_links()[1]
		state[1] = thread_links
		state[4] = i_thread
		print "\nOn subforum page %d: %s" %(i_page, br.geturl()) 
	while i_thread < len(thread_links):
		t_link, t_title = thread_links[i_thread]
		#crawl thread
		r = request_page(t_link)
		if state[3] == i_page and state[4] == i_thread and state[5] is not None:
			i_tpage = state[5]
			t_page_links = state[2]
			print "Resuming scrape on thread page %d" % i_tpage
		else:
			print "Opening thread %s" % t_title
			t_link_base = re.split(r"\.html", t_link)[0]
			#get thread page links
			t_page_links = []
			for link in br.links():
				if link.attrs and link.attrs[0] and link.attrs[0][1]:
					url = link.attrs[0][1]
				if url.startswith(t_link_base):
					t_page_links.append(url)

			t_page_links = sorted(list(set(t_page_links)), key=lambda x: int(re_sort.findall(x)[0]))
			
			i_tpage = -1
			state[2] = t_page_links
			state[5] = i_tpage
		while i_tpage < len(t_page_links):
			fo = open(sdir + "thread%d_%d" % (i_thread+1,i_tpage+2), 'w')
			if i_tpage != -1:
				r = request_page(t_page_links[i_tpage])
			src = r.read()
			
			fo.write(src)
			i_tpage+=1
		print "finished thread %d" %i_thread
		i_thread+=1
	print "finished subforum page %d" %i_page
	i_page+=1

#print results
