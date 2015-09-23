#inspired by and a derivate of reddit's scraper.py
from bs4 import BeautifulSoup
from django.core.validators import URLValidator
from urlparse import urlparse, urljoin
from django.core.exceptions import ValidationError
import urllib, urllib2, re, requests, sys, StringIO#, cStringIO
from urllib2 import Request, urlopen
from PIL import Image, ImageFile
from io import BytesIO
import os, httplib2, math
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")

urlv = URLValidator()
bytes_read = 0
thumbnail_size = 70, 70
hdr= {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}

def final_url(url):
	global bytes_read
	h = httplib2.Http(".cache_httplib")
	bytes_read = bytes_read + sys.getsizeof(h)
	h.follow_all_redirects = True
	resp = h.request(url, "GET")[0]
	bytes_read = bytes_read + sys.getsizeof(resp)
	contentLocation = resp['content-location']
	return contentLocation
'''
def unshorten_url(url):
	parse_object = urlparse(url)
	h = httplib.HTTPConnection(parse_object.netloc)
	h.request('HEAD', parse_object.path)
	response = h.getresponse()
	print response
	print url
	if response.status/100 == 3 and response.getheader('Location'):
		return unshorten_url(response.getheader('Location'))
	else:
		return url
'''
def isyoutube(url):
	if ('youtube' or 'youtu.be') in url:
		vid_id = re.search(r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)", url)
		try:
			return 'i1.ytimg.com/vi/%s/mqdefault.jpg' % vid_id.group()
		except Exception as e:
			print 'isyoutube():there was no video ID in the youtube URL'
			return 0
	else:
		#not a youtube URL
		return 0

def parse_url(url):
	global bytes_read
	#r = requests.get(url)
	#bytes_read = bytes_read + sys.getsizeof(r)
	#url = r.url
	parse_object = urlparse(url)
	if not parse_object.scheme:
		url = "http://"+url
	#url = urlnorm.norm(url)
	finalurl = final_url(url)
	youtube_video_link = isyoutube(finalurl)
	if youtube_video_link:
		finalurl = temp
		return (finalurl, 0)
	try:
		#url = urllib2.urlopen(url).geturl()
		req = urllib2.Request(url, None, headers=hdr)
		bytes_read = bytes_read + sys.getsizeof(req)
		webpage = urllib2.urlopen(req) #urllib2 is an http library
		bytes_read = bytes_read + sys.getsizeof(webpage)
		#url2 = webpage.url # is huge, need to go a head request instead. 
		if url==finalurl:
			#print url
			content_type = webpage.headers.get('content-type')
			if 'image' in content_type:
				return (url, 0)
			soup = BeautifulSoup(webpage, "lxml")
			return (url, soup)
		else:
			#print finalurl
			req2 = urllib2.Request(finalurl, None, headers=hdr)
			bytes_read = bytes_read + sys.getsizeof(req2)
			webpage2 = urllib2.urlopen(req2)
			bytes_read = bytes_read + sys.getsizeof(webpage2)
			content_type = webpage2.headers.get('content-type')
			if 'image' in content_type:
				return (finalurl, 0)
			soup = BeautifulSoup(webpage2, "lxml")
			return (finalurl, soup)
	except Exception as e:
		print str(e)
		return (0, 0)

def clean_url(url):
	"""clean_url quotes unicode data out of urls"""
	s = url
	url = s.encode('utf8')
	url = ''.join([urllib.quote(c) if ord(c) >= 127 else c for c in url])
	#print url
	return url

def image_sizing(string, url):
	RANGE = 5000
	src = string.get("src")
	clean_src = clean_url(src)
	global bytes_read
	try:
		urlv(clean_src)
		print 'the validated url is %s' % clean_src
	except:
		print 'image_sizing(): found URL fragment, attempting urljoin() with parent URL'
		clean_src = urljoin(url, clean_src)
		clean_src = clean_url(clean_src)
		print 'joined_url is %s' % clean_src
	try:
		print 'bytes read before requesting URL %s' % bytes_read
		req  = requests.get(clean_src,headers={'User-Agent':'Mozilla5.0(Google spider)','Range':'bytes=0-{}'.format(RANGE)})#requests is an HTTP library
		bytes_read = bytes_read + sys.getsizeof(req)
		print 'bytes read after requesting URL %s' % bytes_read
	except:
		print 'image_sizing(): unable to send http request to url'
	try:	
		dimensions = Image.open(BytesIO(req.content))#bytesIO is a simple stream of in-memory bytes, open doesn't load image
		return (dimensions, clean_src)
		#return (im.size, clean_src)
	except Exception as e:
		print 'image_sizing(): unable to obtain image dimensions'
		return (None, None)	

def return_largest_image(url):
	normal_url, soup = parse_url(url)
	#is normal_url an image file?
	max_area = 0
	max_dimensions = None
	max_clean_src = None
	previous_max_src = None
	if normal_url:
		if soup:
			for img in soup.findAll('img', limit=40, src=True):
				my_dimensions, my_clean_src = image_sizing(img, normal_url)
				#what do we do when dimensions are zero but image exists? (e.g. http://bollywood007.com/veena-malik-pics.html/veena-malik-nude-randi-pics)
				try:
					if my_dimensions.height * my_dimensions.width < 5001:#ignore small images
						continue
					if my_dimensions.height/my_dimensions.width>1.5:#ignore banner like images
						continue
					if my_dimensions.width/my_dimensions.height>1.5:#ignore banner like images
						continue
					return my_clean_src
					'''
					area = my_dimensions.height * my_dimensions.width
					if area > max_area:
						max_area = area
						#print 'assigning previous'
						previous_max_src = max_clean_src #assigning previously biggest image to previous_max_src
						max_dimensions = my_dimensions
						max_clean_src = my_clean_src
					'''
				except Exception as e:
					print 'return_largest_image(): found non-image object while looping through soup.findAll'
					continue	
		else:
			max_clean_src = normal_url #if soup = 0, the url is an image url itself
	#if max_clean_src: print max_clean_src
	#if max_dimensions: print max_dimensions
	return max_clean_src#, previous_max_src)
	
def image_entropy(img):
	"""calculate the entropy of an image"""
	hist = img.histogram()
	hist_size = sum(hist)
	hist = [float(h) / hist_size for h in hist]
	return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_image(img):
	"""if the image is taller than it is wide, square it off. determine
	which pieces to cut off based on the entropy pieces."""
	x,y = img.size
	while y > x:
		#slice 10px at a time until square
		slice_height = min(y - x, 10)
		bottom = img.crop((0, y - slice_height, x, y))
		top = img.crop((0, 0, x, slice_height))
		#remove the slice with the least entropy
		if image_entropy(bottom) < image_entropy(top):
			img = img.crop((0, 0, x, y - slice_height))
		else:
			img = img.crop((0, slice_height, x, y))
		x,y = img.size
	return img

def prep_image(image):
	image = square_image(image)
	global thumbnail_size
	try:
		image.thumbnail(thumbnail_size)#, Image.ANTIALIAS)
		#print 'successfully thumbnailed'
		return image
	except Exception as e:
		print 'prep_image(): unable to successfully thumbnail image'
		return 0


def str_to_image(s):
	s = StringIO.StringIO(s)
	s.seek(0)
	image = Image.open(s)
	return image

def imagifier(url):
	global bytes_read
	if url:
		url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
		print url
		name = urlparse(url).path.split('/')[-1]
		name = name.replace(' ', '')
		print name
		try:
			open_req = urlopen(url)
			bytes_read = bytes_read + sys.getsizeof(open_req)
			content = open_req.read()
			bytes_read = bytes_read + sys.getsizeof(content)
			print bytes_read
		except:
			print 'imagifier(): recieved url, but unable to open and read it'
			return (None, None)
		try:	
			image = str_to_image(content)
		except:
			print 'imagifier(): recieved, opened and read url, but unable to str_to_image() it'
			return (None, None)
		try:
			image = prep_image(image)
			return (name,image)
		except Exception as e:
			print 'imagifier(): recieved, opened and read url, but unable to prep_image()'
			return (None, None)
	else:
		print 'imagifier(): did not recieve image url'
		return (None, None)


def read_image(url):
	src= return_largest_image(url)
	return imagifier(src)

if __name__=="__main__":
		read_image()