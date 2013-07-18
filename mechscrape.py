#!/usr/bin/env python
import mechanize
import cookielib
import re
import sys
import signal
import atexit
import pickle

from BeautifulSoup import BeautifulSoup as bs

#import dblib

state = []
re_sort = re.compile(r"\d*(?=\.html)")
re_uid = re.compile(r"\d*$")
i_page = None
i_thread = None
i_tpage = None
i = None

def write_to_file(of, t_title, t_link, body, start):
	assert of
	if start:
		prepend = '***subforum_page:%s, thread:%s\n' % (i_page+2, i_thread+1)
		prepend += '**thread_page:%s\n' % (i_tpage)
		prepend += 'thread_title:%s\n'%t_title
		prepend += 'thread_link:%s\n\n'%t_link
	else:
		prepend = '\n**thread_page:%s\n' % (i_tpage)
	out_string = prepend+body+'\n'
	
	of.write(out_string)

def interrupt(signal, frame):
	sys.exit(0)

def _save_state():
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

def get_links(br):
	"""
	get_links(br)
	input: mechanize browser object
	gets all thread links and page links from myBB style forum archive page
	returns: (page_links, thread_links)
	where each thread_link is a tuple of (url, title)
	"""
	assert br

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
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
"""
try:
cj.load("cookie123")
print "Cookie loaded"
except:
"""
#Login
print "(Cookie not found. Logging in!)"
r = br.open('http://www.hackforums.net/showthread.php?tid=3622698')
br.select_form(nr=0)
br["username"] = "cant_buy_me_love"
br["password"] = "aZerba1Jan"
results = br.submit().read()
cj.save("cookie123")

sublink = "http://www.hackforums.net/archive/index.php/forum-114.html"
r = br.open(sublink)
cur_page = br.geturl()

page_links, thread_links = get_links(br)


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
	fo = open("hackscrapes/hackforums%d.out" %(i_page+2), "a")
	if i_page == state[3] and state[4] is not None: #state[4] is i_thread
		thread_links = state[1]
		i_thread = state[4]
		print "Resuming scrape on thread %d" % i_thread
	else:
		i_thread = 0
		state[4] = i_thread
	if i_page!=-1: #skip first time
		r = br.open(page_links[i_page])
		thread_links = get_links(br)[1]
		state[1] = thread_links
		state[4] = i_thread
		print "On thread page %d: %s" %(i_page, br.geturl()) 
	while i_thread < len(thread_links):
		t_link, t_title = thread_links[i_thread]
		#crawl thread
		r = br.open(t_link)
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
		firstpage = True 
		while i_tpage < len(t_page_links):
			if i_tpage != -1:
				r = br.open(t_page_links[i_tpage])
			src = r.read()
			print "On page %d: %s" % (i_tpage+2, br.geturl())
			b = bs(src)
			posts = b.findAll('div', attrs={'class':'post'})
			if not posts:
				print "Error: No posts on page %s" % br.geturl()
				sys.exit(0)
				continue
			i = 0
			pagetxt = "page:%s\n" % br.geturl()
			while i < len(posts):
				p = posts[i]
				raw_auth = p.find('div', attrs={'class':'author'})
				if not raw_auth or not raw_auth.text:
					print "Error: No author on post %d on page %d" % (i, i_tpage)
					continue
				auth = raw_auth.text.encode('utf8')
				raw_auth_link = raw_auth.find('a')
				if raw_auth_link and raw_auth_link.has_key('href'):
					auth_link = raw_auth_link['href'].encode('utf8')
					auth_id = re.findall(re_uid, auth_link)[0]
				else:
					auth_link = ""
					auth_id = ""
				raw_dateline = p.find('div', attrs={'class':'dateline'})
				if not raw_dateline or not raw_dateline.text:
					print "Error: No dateline on post %d on page %d" % (i, i_tpage)
					continue
				dateline = raw_dateline.text.encode('utf8')

				message = p.find('div', attrs={'class':'message'})
				if not message:
					print "Error: No message on post %d on page %d" % (i, i_tpage)
					continue 
				#imgs = message.findAll("img")
				#img_links = []
				#for j, img in enumerate(imgs):
				#	try:
				#		img_links.append(img['src'])
				#	except:
				#		print "Error: Image %d from post %d on page %d has no source" % (j, i, i_tpage)
				#		#dbp = dblib.post(
				
				#post_id, user_id = dblib.insert_data(con, cur, dbp)
				post = "*post:%d\n%s\n%s\t%s\n%s\n" % \
					(i,dateline,auth,auth_id,message.renderContents().encode("string_escape"))
				pagetxt += post 
				
				i+=1
			if i_tpage == len(t_page_links)-1:
				lastpage=True
			write_to_file(fo, t_title, br.geturl(), pagetxt, firstpage)
			firstpage=False
			i_tpage+=1
		print "finished thread %d" %i_thread
		i_thread+=1
	print "finished subforum page %d" %i_page
	i_page+=1

#print results
