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
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import urlparse
from urlparse import urljoin
import subprocess

#import dblib

state = []
re_sort = re.compile(r"\d*(?=\.html)")
re_uid = re.compile(r"\d*$")
i_page = None
i_thread = None
i_tpage = None
i = None
save_file = ""
use_selenium = True

timeout=5

def init_selenium():
	profile = webdriver.FirefoxProfile("profile.hackforums")
	br = webdriver.Firefox(profile)
	br.set_page_load_timeout(timeout)
	return br

def init_browser():
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

def send_esc(br):
	p = subprocess.Popen(["xdotool", "search", "--all", "--pid", str(br.binary.process.pid), "--name", "Mozilla Firefox", "key", "Escape"])

def visit_page(br, page):
	global timeout
	if use_selenium:
			try:
				br.get(page)
			except TimeoutException:
				send_esc(br)
	else:
		tries = 0
		while tries < 10:
			try:
				br.open(page)
				return
			except Exception as e:
				print "Error: %s" % e.code
				tries+=1
				time.sleep(10)
		print "Fatal error. Restarting browser."
		br = init_browser()
		sys.exit(0)	

def interrupt(signal, frame):
	sys.exit(0)

def save_state():
	f = open(save_file, "w")
	print "EXITING. SAVING STATE TO FILE."
	state[3] = i_page
	state[4] = i_thread
	state[5] = i_tpage
	pickle.dump(state, f)
	f.close()
	print "subforum page = %s\n\
	thread # = %s\n\
	thread page # = %s" % (state[3], state[4], state[5])

def get_urls(br):
	raw_urls = []
	if use_selenium:
		src = br.page_source
		soup = bs(src)
		for a in soup.findAll('a', href=True):
			raw_urls.append(urlparse.urljoin(sublink, a['href']))
	else:
		for link in br.links():
			raw_urls.append(link)
	return raw_urls
def get_links(br):
	"""
	get_links(br)
	input: browser object
	gets all thread links and page links from myBB style forum archive page
	returns: (page_links, thread_links)
	where each thread_link is a tuple of (url, title)
	"""
	raw_urls = get_urls(br)
	retries = 0
	while not raw_urls:
		link = br.current_url
		br.quit()
		print "get_link failed. restarting browser..."
		br = init_browser()
		visit_page(br, link)
		sleep(10)
		raw_urls = get_urls(br)
	plx = []
	tlx = []
	for url in raw_urls:
		if re.search(r"/archive/index\.php/forum-114-", url):
			plx.append(url)
		if re.search(r"/archive/index\.php/thread-", url):
			tlx.append(url)
	plx = sorted(list(set(plx)), key=lambda x: int(re_sort.findall(x)[0]))
	return plx, tlx


if len(sys.argv) < 6:
	print "Usage: python progname.py dir link ipage part parts"

homedir = sys.argv[1]
sublink = sys.argv[2]
i_page = int(sys.argv[3])
part = int(sys.argv[4])
parts = int(sys.argv[5])
save_file = ".hackforums%d-%d.p"%(part,parts)#sys.argv[3]
#homedir = "hackdumps/"
#sublink = "http://www.hackforums.net/archive/index.php/forum-114.html"

atexit.register(save_state)

try:
	f = open(save_file, "rw")
	state = pickle.load(f)
except:
	state = [None]*6
	print "No save file found. Initiating new scrape."

if use_selenium:
	br = init_selenium()
else:
	br = init_browser()

visit_page(br, sublink)
time.sleep(10)
page_links, thread_links = get_links(br) 

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

i_page = i_page+(part-1)*((len(page_links)-i_page)/parts)
end_ind = i_page+part*((len(page_links)-i_page)/parts)

print "Scrape part %d of %d: %d-%d" %(part,parts,i_page,end_ind)

if state[3] is not None:
	#i_page
	i_page = state[3]
	print "Resuming scrape on subforum page %d" % i_page
else:
	state[3] = i_page

while i_page < end_ind:
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
		visit_page(br, page_links[i_page])
		thread_links = get_links(br)[1]
		state[1] = thread_links
		state[4] = i_thread
		print "\nOn subforum page %d: %s" %(i_page, page_links[i_page]) 
	while i_thread < len(thread_links):
		t_link = thread_links[i_thread]
		#crawl thread
		visit_page(br, t_link)
		if state[3] == i_page and state[4] == i_thread and state[5] is not None:
			i_tpage = state[5]
			t_page_links = state[2]
			print "Resuming scrape on thread page %d" % i_tpage
		else:
			print "Opening thread %s" % t_link 
			t_link_base = re.split(r"\.html", t_link)[0]
			#get thread page links
			t_page_links = []
			raw_urls = get_urls(br)
			for url in raw_urls:
				if url.startswith(t_link_base):
					t_page_links.append(url)
			t_page_links = sorted(list(set(t_page_links)), key=lambda x: int(re_sort.findall(x)[0]))
			
			i_tpage = -1
			state[2] = t_page_links
			state[5] = i_tpage
		while i_tpage < len(t_page_links):
			fo = open(sdir + "thread%d_%d" % (i_thread+1,i_tpage+2), 'w')
			if i_tpage != -1:
				visit_page(br, t_page_links[i_tpage])
			if use_selenium:
				src = br.page_source
			else:
				src = br.response.read()
			
			fo.write(src.encode('utf8'))
			i_tpage+=1
		print "finished thread %d" %i_thread
		i_thread+=1
	print "finished subforum page %d" %i_page
	i_page+=1

#print results
