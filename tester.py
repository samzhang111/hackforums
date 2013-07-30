from BeautifulSoup import BeautifulSoup as bs
from math import sqrt
import sys
import re

def mean(li):
    """
    mean(list)

    returns mean of a list of integers (float)

    """

    return float(sum(li))/len(li)

def std(li):
    """
    std(list)

    returns standard deviation of list of integers (float)

    """
    m = mean(li)
    return sqrt(mean([abs(x-m) for x in li]))

def strip_links(L):
    """strip_links(L)
    Takes all BeautifulSoup tags at a certain depth level.
    Returns the list, without the links.

    """
    return filter(lambda x: x.name!='a', L)

def get_tags_by_depth(soup):
	"""get_tags_by_depth(soup)
	Takes a BeautifulSoup object. Returns a list [d0, d1, ..., dn],
	where di is a list of all tags at that given depth level.
	Eg d0=[head, body]
	d1=[meta, table, script]
	Note: the lists will not print out the names, because they contain all the children below them as well.
	To print out the names, call pn(di), and to print out first attributes, call pa(di)

	"""
	tags = soup.findAll()
	if not tags:
		return []
	tags_by_depth = [soup.findAll()[0].findChildren(recursive=False)]
	d = 1
	while True:
		tags = []
		for t in tags_by_depth[d-1]:
			tags.extend(t.findChildren(recursive=False))
	
		tags = filter(None, tags)
		if tags:
			tags_by_depth.append(tags)
		else:
			return tags_by_depth
		
		d+=1

def tag_distribution(L):
	"""tag_distribution(L):
	Takes all BeautifulSoup tags at a certain depth level.
	Returns a dictionary of counts for each tag-attr.
	Strips all links.
	Replaces all series of numbers with a single x.

	E.g. [BeautifulSoup("<div class=post32124></div>")] returns {'div-postx': 1}

	"""
	ud = {}
	for x in L:
		n = name_attr(x)
		if n:
			if n in ud.keys():
				ud[n] += 1
			else:
				ud[n] = 1
	return ud

def similarity(L1, L2):
    """ similarity(L1, L2)
    Takes two lists of BeautifulSoup tags
    Returns the number of UNIQUE name-attr pairs that are not shared by both

    """
    d1 = tag_distribution(L1)
    d2 = tag_distribution(L2)
    mismatches = 0
    for k1 in d1.keys():
		if k1 not in d2.keys():
			mismatches += 1 

    for k2 in d2.keys():
		if k2 not in d1.keys():
			mismatches += 1

    return float(mismatches)/(len(d1.keys())+len(d2.keys()))


def name_attr(tag, strip_nums=1, strip_orphans=1, strip_links=1):
    """name_attr(tag, strip_nums=1, strip_orphans=1, strip_links=1)
    Takes a BeautifulSoup tag.
    Returns a string formatted "name-first_attribute-second_attribute".
    E.g. [<div class="post" style="font-weight:normal"></div>] returns "div-post-font-weight:normal"
    
    strip_nums: strips the numbers from the attribute, replacing any series of them with a single "x"
    E.g. [<div class=post232></div>] returns "div-postx"

    strip_orphans: returns an empty string for any tag that doesn't have attributes.
    
    strip_links: returns an empty string for any link tags.
    
    """
    if not strip_links or tag.name!= 'a':
		if not strip_orphans or tag.attrs:
			at = [tag.attrs[i][1] for i in xrange(len(tag.attrs))]
			at = "-".join(at)
			if strip_nums:
				at = re.sub(r"\d+","x", at)
			return "%s-%s"%(tag.name, at)
    return ""

def pn(L):
    """pn(L):
    (print name)
    Takes all BeautifulSoup tags at a certain depth level.
    Calls name_attr() on all of them.

    """
    return filter(None, map(name_attr, L))

def of(name, num, suffix=""):
    soups = []
    for i in xrange(1, int(num)+1):
		soups.append(bs(open("%s%s%s"%(name,str(i),suffix)).read()))
    return soups

def get_outliars(dic):
	"""get_outliars(dictionary)
	Takes a dictionary where the values are integer counts.
	Returns the keys where the values are two standard deviations above the mean.

	"""
	m = mean(dic.values())
	s = std(dic.values())
	k = filter(lambda x: x[1] > m + 2*s, dic.items())
	if k:
		return zip(*k)[0]

def get_tags_by_outliar(na, L):
    """get_tags_by_outliar(string, list of BS tags)
    Takes a name-attr string (as specified in name_attr()) and returns tags that match

    """
    
    return filter(lambda x: name_attr(x)==na, L)

def get_outliars_by_depth(tbd, d, i):
	"""get_outliars_by_depth(tags_by_depth, depth, index)
	Returns all outliar tags by depth and index. List of lists.

	"""
	outliars = get_outliars(tag_distribution(tbd[d][i]))
	if not outliars:
		return []
	out_tags = [get_tags_by_outliar(x, tbd[d][i]) for x in outliars]
	return out_tags

if len(sys.argv) < 4:
	print "usage: python tester.py dir # suffix"

soups = of(sys.argv[1], sys.argv[2], sys.argv[3])
tbd = map(get_tags_by_depth, soups)
tbd = zip(*tbd)
if len(tbd) < 3:
    print "Min depth not achieved."
    sys.exit()
for i in range(3, len(tbd)-1):
    sim_matrix = [similarity(x1, x2) for x1 in tbd[i] for x2 in tbd[i]]
    print i, std(map(len, tbd[i]))
    if sum(sim_matrix) != 0:
		print "No longer closely related."
		break

t1 = [get_outliars_by_depth(tbd, i-1, x) for x in xrange(len(tbd[0]))]
t2 = [get_outliars_by_depth(tbd, i  , x) for x in xrange(len(tbd[0]))]
t3 = [get_outliars_by_depth(tbd, i+1, x) for x in xrange(len(tbd[0]))]

