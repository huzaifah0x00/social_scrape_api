"""
	This program implements apis to get a person's stats(friends/followers count, total posts, posts made in the last x days) from their social media page
"""


import sys
import json
import requests
import tweepy
import time 
import re

###DEPS FOR FACEBOOK
from datetime import datetime
# from bs4 import BeautifulSoup as BS
from lxml import etree
import requests


# from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys

###DEPS FOR FACEBOOK 


from copy import deepcopy
from hashlib import md5

#A class for exception handling when the username is invalid ( facebook )
class InvalidUsername(BaseException):
	pass

class Facebook:
	"""methods : get_friends_count(self, user_page), get_no_of_posts

	"""

	def __init__(self, username, password):
		self.login_username = username
		self.login_password = password
		self.fb_url = 'http://m.facebook.com'
		# self.options = Options()
		# self.options.headless = True # uncomment to hide firefox window 
		# self.driver = webdriver.Firefox(options=self.options)
		self.session = requests.Session()
		
		# self.driver.get(self.fb_url)
		# email = self.driver.find_element_by_id('m_login_email')
		# password = self.driver.find_element_by_name('pass')

		# email.send_keys(self.login_username)
		# password.send_keys(self.login_password)

		# self.driver.find_element_by_name('login').click()
		login_url = "https://m.facebook.com:443/login/device-based/regular/login/"
		user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/58.0.1"}
		login_data={"email": self.login_username, "pass": self.login_password, "login": "Log In"}
		self.session.post(login_url, headers=user_agent, data=login_data)




	def is_older_than(self,post_date, maxdays):
		"""this function checks if the first param post_date
				is older(less than the maxdays)"""

		##there's three possible formats for a date on facebook's post..
		# 26 December 2017 at 19:49
		# 13 January at 00:50

		# 10 hrs

		#count the whitespaces... to convert it into datetime object
		month = {
				'January' : 1,
				'February' : 2,
				'March' : 3,
				'April' : 4,
				'May' : 5,
				'June' : 6,
				'July' : 7,
				'August' : 8,
				'September' : 9,
				'October' : 10,
				'November' : 11,
				'December' : 12	
				}

		post_date = post_date.split(' ')
		try:
			post_date.remove('at')			
		except:
			pass
		try:
			post_date.remove('AM')
		except:
			pass
		try:
			post_date.remove('PM')
		except:
			pass
		post_date = [i.strip(',') for i in post_date]

		now = datetime.now()
		# if len(post_date) == 4:
		# 	post_date = {
		# 		'date' : int(post_date[0]),
		# 		'month' : month[post_date[1]],
		# 		'year' : int(post_date[2]),
		# 	}
		# elif len(post_date) == 3:
		# 	post_date = {
		# 		'date' : int(post_date[0]),
		# 		'month' : month[post_date[1]],
		# 		'year' :  now.year,
		# 	}
		# elif len(post_date) == 2:
		# 	post_date = {
		# 		'date' : now.day ,
		# 		'month' : now.month ,
		# 		'year' :  now.year,
		# 		}
		# else:
		# 	print(f"UNDEFINED SORT OF DATE {post_date}")
		# print(f"POST DATE : {post_date}")
		if len(post_date) == 4:
			post_date = {
				'date' : int(post_date[1]),
				'month' : month[post_date[0]],
				'year' : int(post_date[2]),
			}
		elif len(post_date) == 3:
			post_date = {
				'date' : int(post_date[1]),
				'month' : month[post_date[0]],
				'year' :  now.year,
			}
		elif len(post_date) == 2:
			post_date = {
				'date' : now.day ,
				'month' : now.month ,
				'year' :  now.year,
				}
		else:
			print(f"UNDEFINED SORT OF DATE {post_date}")

		days = now.day - post_date['date']
		months = now.month - post_date['month']
		years = now.year - post_date['year']

		days_since = int(days+(months*30.42)+(years*365.25))

		if days_since > maxdays:
			return False
		else:
			return True

	# def get_followers_count(self):
	# 	pass

	def get_friends_count(self, username):
		# self.friends_count = self.driver.get()
		self.page_url = "https://m.facebook.com/"+username
		user_page = self.session.get(self.page_url)
		# if user_page.url != self.page_url:
		# 	print("URL MISMATCH: current: {}\n\tactual: {}".format(user_page.url, self.page_url))
		# 	print("probably 404 check the profile url")
		# 	return 1
		try:
			user_page_parsed = etree.XML(user_page.content, etree.HTMLParser())
			timeline_link = user_page_parsed.xpath("//div/a[contains(text(), 'Timeline')]")[0].get('href')
			timeline_link = "https://m.facebook.com"+timeline_link

			# timeline = self.driver.find_element_by_xpath("//div/a[contains(text(), 'Timeline')]")
		except IndexError:
			print("they dont have a timeline link ")
			# return 1;

		user_page_parsed = etree.XML(user_page.content, etree.HTMLParser())
		# friends_page = self.driver.find_element_by_xpath("//div/a[contains(text(), 'Friends')]")
		
		try:
			# friends_page = self.driver.find_element_by_css_selector("a[href*='/friends?']")
			friends_page_url = user_page_parsed.cssselect("a[href*='/friends?']")[0].get('href')
			friends_page_url = 'https://m.facebook.com' + friends_page_url
			friends_page = self.session.get(friends_page_url)
			friends_page_parsed = etree.XML(friends_page.content, etree.HTMLParser()) 
		except IndexError:
			print(user_page_parsed.text)
			print("something went wrong. maybe they don't have friends? ")
			raise
			return "not_available"

		try:
			# friends_count = self.driver.find_element_by_css_selector('h3')
			friends_count = friends_page_parsed.cssselect('h3')[0]
			friends_count = re.search('Friends \((?P<count>.+)\)',friends_count.text).group('count')
		except IndexError:
			# print(f"No Friends For {self.driver.current_url}")
			print(f"No Friends For {user_page.url}")
			friends_count = 0
		# print(friends_count.text)

		return friends_count

	def next_page_timeline(self,next_page_url):
		# user_page = session.get(next_page_url)
		# user_page_parsed = etree.XML(user_page.content, etree.HTMLParser())
		# # likes_string = user_page_parsed.xpath("//head/meta[contains(@name, 'description')]")
		# # likes_count = re.search('(?P<num>[0-9,.KM]+) likes',likes_string).group('num')

		# timeline_link = user_page_parsed.xpath("//div/a[contains(text(), 'Timeline')]")[0].get('href')
		# timeline_link = "https://m.facebook.com"+timeline_link
		timeline_page = self.session.get(next_page_url)
		timeline_page_parsed = etree.XML(timeline_page.content, etree.HTMLParser())
		return timeline_page_parsed

	def get_no_of_posts(self,username, maxdays ):
		self.username = username
		self.page_url = "https://m.facebook.com/"+username
		next_page_url = True
		# self.driver.get(self.page_url)
		user_page = self.session.get(self.page_url)

		
		if user_page.url != self.page_url:
			print("URL MISMATCH: current: {}\n\tactual: {}".format(user_page.url, self.page_url))
			self.likes_count = "error"
			return "error"

		is_profile = False
		try:
			user_page_parsed = etree.XML(user_page.content, etree.HTMLParser())
			timeline_link = user_page_parsed.xpath("//div/a[contains(text(), 'Timeline')]")[0].get('href')
			timeline_link = "https://m.facebook.com"+timeline_link

			# timeline = self.driver.find_element_by_xpath("//div/a[contains(text(), 'Timeline')]")
			is_profile = True
		except IndexError:
			# print("is_page")
			pass

		if is_profile:
			self.likes_count = "is_profile"
			# self.friends_count = self.get_friends_count(user_page)
			#timeline.click()
			timeline_page = self.session.get(timeline_link)
			timeline_page_parsed = etree.XML(timeline_page.content, etree.HTMLParser())

		else:
			try:

				# likes_string = self.driver.find_element(By.XPATH, "//head/meta[contains(@name, 'description')]").get_attribute("content")
				likes_string = user_page_parsed.xpath("//head/meta[contains(@name, 'description')]")[0].attrib['content']

				#Ongina, onginabookings@gmail.com. 61K likes. Ladyboy at its best!
				self.likes_count = re.search('(?P<num>[0-9,.KM]+) likes',likes_string).group('num')

				# self.likes_count = self.likes_count.split('.')[1].split('likes')[0].strip()
				self.likes_count = self.likes_count.replace(',', '')
				# .replace('K', '000').replace('M', '000000')
				if 'K' in self.likes_count:
					self.likes_count = int(float(self.likes_count.strip('K'))*1000)
				elif 'M' in self.likes_count:
					self.likes_count = int(float(self.likes_count.strip('M'))*1000000)
				else:
					self.likes_count = int(self.likes_count)

				# print("likes count: "+ str(self.likes_count))
			except IndexError:
				print("Probably 404 {}".format(self.page_url))
				self.likes_count = "error"
				return ""
			except AttributeError:
				print("Error determining likes... not logged in? ")
				raise


		posts_count = 0
		while True:
			if next_page_url:
				# time.sleep(3) # delay for avoiding block by facebook?
				xpaths = {
					"show_more" : "//div[contains(@class, j)]/a[contains(text(), 'Show more')]",
					"post" : "./div/div/div/div[contains(@id, 'u_0_')]",
					# "date" : ".//div/abbr"
				}
				if is_profile:
					# xpaths['show_more'] = "//div[contains(@class, j)]/a/span[contains(text(), 'See more stories')]"
					xpaths['show_more'] = "//div[contains(@class, j)]/a/span[contains(text(), 'See More Stories')]"
					xpaths['post'] = "./div/div[contains(@id, 'u_0_')]"

				try:
					# timeline = self.driver.find_element_by_css_selector('#timelineBody')
					# timeline = self.driver.find_element_by_css_selector('#structured_composer_async_container')
					timeline = timeline_page_parsed.cssselect('#structured_composer_async_container')[0]
				except UnboundLocalError:
					timeline = user_page_parsed.cssselect('#structured_composer_async_container')[0]
				


				# all_posts_on_page = timeline.find_elements(By.XPATH, xpaths['post'])
				all_posts_on_page = timeline.xpath(xpaths['post'])
				for post in all_posts_on_page:
					# post_date = post.find_element(By.XPATH, date_xpath)
					try:
						# post_date = post.find_element_by_tag_name('abbr').text
						post_date = post.find('.//abbr').text
					except:
						print("err getting date")
						post_date = "error"
						continue

					if self.is_older_than(post_date, maxdays):
						posts_count += 1 
					else:
						return posts_count
				try:
					# next_page = self.driver.find_element(By.XPATH, xpaths['show_more'])
					next_page = timeline.xpath(xpaths['show_more'])[0]
					if is_profile:
						next_page_url = 'https://m.facebook.com' + next_page.getparent().get('href')
					else:
						next_page_url = 'https://m.facebook.com' + next_page.get('href')
				except :
					raise
					print("Problem ? with {}".format(self.page_url))
					break
				# next_page.click()
				timeline_page_parsed = self.next_page_timeline(next_page_url)
			else:
				# print("No More Pages")
				break
	def get_likes_count(self,username, maxdays ):
		self.username = username
		self.page_url = "https://m.facebook.com/"+username
		user_page = self.session.get(self.page_url)

		
		if user_page.url != self.page_url:
			print("URL MISMATCH: current: {}\n\tactual: {}".format(user_page.url, self.page_url))

			self.likes_count = "error"
			print("probably 404 check the profile url")
			return 1

		is_profile = False
		try:
			user_page_parsed = etree.XML(user_page.content, etree.HTMLParser())

			# timeline = self.driver.find_element_by_xpath("//div/a[contains(text(), 'Timeline')]")
			is_profile = True
		except IndexError:
			# print("is_page")
			pass

		if is_profile:
			self.likes_count = "is_profile"

		else:
			try:

				# likes_string = self.driver.find_element(By.XPATH, "//head/meta[contains(@name, 'description')]").get_attribute("content")
				likes_string = user_page_parsed.xpath("//head/meta[contains(@name, 'description')]")[0].attrib['content']

				#Ongina, onginabookings@gmail.com. 61K likes. Ladyboy at its best!
				self.likes_count = re.search('(?P<num>[0-9,.KM]+) likes',likes_string).group('num')

				# self.likes_count = self.likes_count.split('.')[1].split('likes')[0].strip()
				self.likes_count = self.likes_count.replace(',', '')
				# .replace('K', '000').replace('M', '000000')
				if 'K' in self.likes_count:
					self.likes_count = int(float(self.likes_count.strip('K'))*1000)
				elif 'M' in self.likes_count:
					self.likes_count = int(float(self.likes_count.strip('M'))*1000000)
				else:
					self.likes_count = int(self.likes_count)

				# print("likes count: "+ str(self.likes_count))
			except IndexError:
				print("Probably 404 {}".format(self.page_url))
				self.likes_count = "error"
				return ""
			except AttributeError:
				print("Error determining likes... not logged in? ")
				raise

class Instagram():
	""" has these useful methods: get_no_of_posts, get_followers_count
	and a few useful attributes (followers_count, total_posts, no_of_posts_in_days)
	 
	
	 """
	def __init__(self, username):
		self.BASE_URL = "https://www.instagram.com/"
		self.QUERY_HASH = "f412a8bfd8332a76950fefc1da5785ef"
		self.session = requests.Session()
		self.heads = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/58.0.1" }
		self.username = username
		firstresponse=self.session.get(self.BASE_URL + self.username, headers=self.heads)
		if firstresponse.status_code == 404:
			raise InvalidUsername()
		
		self.shared_data = self.get_shared_data()
		self.out_data = self.get_vars(self.shared_data)
		self.acct_id = self.out_data._id
		self.rhx_gis = self.out_data.rhx_gis

		self.total_posts = int(self.out_data.post_count)
		self.followers_count = self.out_data.followers_count

	def get_shared_data(self):
		"""Fetches the user's metadata."""
		_resp = firstresponse.text
		if _resp is not None and '_sharedData' in _resp:
			try:
				_shared_data = _resp.split("window._sharedData = ")[1].split(";</script>")[0]
				return json.loads(_shared_data)
			except (TypeError, KeyError, IndexError):
				raise
				pass
		else:
			print("Failed to get shared data i.e")


	def get_user_data(self,url, headers):
		"""Fetches the user's metadata."""
		time.sleep(0.5) # Add some delay to avoid detection by  instagram?
		_resp = self.session.get(url, headers=headers)

		if _resp is not None:
			try:
				_data = _resp.text
				try:
					_data = json.loads(_data)
				except:
					print("Error with the data : ")
					print(_data)
					return None
					# exit()
				return _data
			except (TypeError, KeyError, IndexError):
				raise


	def gen_gis(self,rhx_gis, variables):
		# variables = "/peakyblindersofficial/"
		string = "{}:{}".format(rhx_gis,variables)
		return md5(bytes(string, encoding='utf-8')).hexdigest()



	def get_vars(self,shared_data):
		class Variables:
			try:
				try:
					userdata = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
				except (KeyError,TypeError):
					try:
						userdata = shared_data['data']['user']
					except:
						print(shared_data)
			except:
				raise

				# print("Error with {}".format(shared_data))
			try:
				is_private = userdata['is_private']
			except KeyError:
				pass
			try:
				followers_count = userdata['edge_followed_by']['count']
			except KeyError:
				pass
			try:
				_id = userdata['id']
			except KeyError:
				pass
			try:
				rhx_gis = shared_data['rhx_gis']
			except KeyError:
				pass

			has_next_page = userdata['edge_owner_to_timeline_media']['page_info']['has_next_page']

			post_count = userdata['edge_owner_to_timeline_media']['count']
			if has_next_page:
				end_cursor = userdata['edge_owner_to_timeline_media']['page_info']['end_cursor'].strip()

		return Variables


	# variables = {'id':}


	def get_no_of_posts(self,maxdays):
		"""Get Number of posts a user has made in X(maxdays) days"""
		counter = 0
		self.no_of_posts_in_days = 0

		first = 12
		self.total_pages = self.posts_count/12.0

		if self.out_data.is_private:
			return "private_acct"
		else:
			while True:
				# if counter == 0:
				# 	shared_data = self.get_shared_data()

				# 	out_data = self.get_vars(shared_data)
				# 	self.acct_id = out_data._id
				# 	first = 12
				# 	self.followers_count = out_data.followers_count
				# 	self.posts_count = int(out_data.post_count)
				# 	self.total_pages = self.posts_count/12.0
				# 	self.rhx_gis = out_data.rhx_gis
				if self.out_data.has_next_page:
					next_variables = {
						"id": self.acct_id,
						"first": first,
						"after": self.out_data.end_cursor,
					}
					next_variables = json.dumps(next_variables, separators=(',', ':'))
					x_insta_gis = self.gen_gis(self.rhx_gis, next_variables)
					headers = {
						"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/58.0.1",
						"Accept": "*/*",
						"Accept-Language": "en-US,en;q=0.5",
						"Accept-Encoding": "gzip, deflate",
						"X-Instagram-GIS": x_insta_gis,  # "f2cfc0e7be5cd74b0ec3318092d60653",
						"X-Requested-With": "XMLHttpRequest",
						"Connection": "close"
					}

					next_url = "https://www.instagram.com:443/graphql/query/?query_hash={}&variables={}"
					next_url = next_url.format(self.QUERY_HASH, next_variables)
					for i in self.out_data.userdata['edge_owner_to_timeline_media']['edges']:
						node = i['node']
						posted_at = node['taken_at_timestamp']
						posted_at = datetime.utcfromtimestamp(posted_at)
						days_old = (datetime.today() - posted_at).days
						if days_old < maxdays:
							self.no_of_posts_in_days += 1
						else:
							return self.no_of_posts_in_days
					resp = self.get_user_data(next_url, headers)
					if resp:
						self.out_data = self.get_vars(resp)
					else:
						pass
				else:
					print("no more pages? ")
					return self.no_of_posts_in_days

				counter += 1
	

class Twitter():
	"""uses the tweepy module to get a user's number of posts in x days
		this only has the numberoftweets_in_days(maxdays) method
	"""
	def __init__(self,screen_name):

		self.screen_name = screen_name
		
		self.followers_count = 0
		self.numberoftweets_in_days = 0

		# self.consumer_key='************'
		# self.consumer_secret='********************'
		# self.access_token_key='********************'
		# self.access_token_secret='********************'

		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token_key, self.access_token_secret)

		self.api = tweepy.API(auth)

	def getnumoftweets_in_days(self, maxdays):
		"""get a user's number of tweets in x days"""
		self.maxdays = int(maxdays)
		self.today = datetime.today()
		self.numberoftweets_in_days = 0
		self.numberofrts_in_days = 0
		for currenttweets in tweepy.Cursor(self.api.user_timeline, count=200,screen_name=self.screen_name,include_rts=True).pages():
			
			self.followers_count = currenttweets[0].user.followers_count
			self.days_since_today = int((self.today - currenttweets[-1].created_at).days)

			if self.days_since_today < self.maxdays: # continue if the last tweet is newer than maxdays
				self.numberoftweets_in_days += len(currenttweets)
			else:
				for i in currenttweets:
					if hasattr(i, 'retweeted_status'):
						is_retweet = True
					else:
						is_retweet = False

					if is_retweet:
						self.days_since_today2 = (self.today - i.created_at).days
						if self.days_since_today2 < self.maxdays:
							self.numberoftweets_in_days += 1
						else:
							return self.numberofrts_in_days,self.numberoftweets_in_days
					else:
						self.days_since_today2 = (self.today - i.created_at).days
						if self.days_since_today2 < self.maxdays:
							self.numberofrts_in_days += 1
						else:
							return self.numberofrts_in_days, self.numberoftweets_in_days
		return self.numberofrts_in_days,self.numberoftweets_in_days

#some useful functions to extract a username from a link
def get_twitter_un(link):
	if link != "N/A":
		try:
			twitter_username = re.search('http(s|)://(www.|mobile.|)twitter.com/(#!/|)(?P<username>[A-Z_0-9.]+)',link, re.IGNORECASE).group('username')
		except:
			print("Error getting username for "+link)
			return "N/A"
	else:
		return "N/A"
	return twitter_username
def get_insta_un(link):
	if link != "N/A":
		try:
			insta_username = re.search('http(s|)://(www.|)instagram.com/(?P<username>[A-Z0-9_.]+)',link, re.IGNORECASE).group('username')
		except AttributeError:
			try:
				insta_username = re.search('http(s|)://(www.|)photostags.com/user/(?P<username>[A-Z0-9_.]+)',link, re.IGNORECASE).group('username')
			except AttributeError:
				return "N/A"
	else:
		return "N/A"
	return insta_username
def get_fb_un(link):
	if link != "N/A":
		try:
			fb_username = re.search('http(s|)://(www.|m.|en-gb.|)facebook.com/(?P<username>[A-Z0-9_./-]+)',link, re.IGNORECASE).group('username')
			return fb_username
		except AttributeError:
			print("err in link {}".format(link))
			return None 

		if 'pages' in link:
			try:
				fb_username = re.search('http(s|)://(www.|m.|en-gb.|)facebook.com/pages/(?P<username>[A-Z0-9_.-]+)',link, re.IGNORECASE).group('username')
			except AttributeError:
				print("LINK WITH pages: {}".format(link))
				return "N/A"
		elif 'people' in link:
			try:
				fb_username = re.search('http(s|)://(www.|m.|en-gb.|)facebook.com/people/(?P<username>[A-Z0-9_.-]+)',link, re.IGNORECASE).group('username')
			except AttributeError:
				print("LINK WITH people: {}".format(link))
				return "N/A"
		else:
			try:
				fb_username = re.search('http(s|)://(www.|m.|en-gb.|)facebook.com/(?P<username>[A-Z0-9_.-]+)',link, re.IGNORECASE).group('username')
			except AttributeError:
				print("LINK WITH .... : {}".format(link))
				return "N/A"
	else:
		return "N/A"
	return fb_username

def main():
	## examples for testing        ...
	facebook_login = {'email': "your email", "pass": "your password"} # because we need to login to view others' profiles

	facebook = Facebook( facebook_login['email'], facebook_login['pass'] )
	facebook.get_no_of_posts("someones_username", maxdays=30) #get num of posts in 30 days

	nobodys_insta = Instagram("nobodys_username")
	print(nobodys_insta.followers_count)
	print(nobodys_insta.no_of_posts_in_days)
	print(nobodys_insta.total_posts)

	## you need to fill in the twitter api keys in the class definition ^^
	nobodys_twitter = Instagram("nobodys_username")
	print(getnumoftweets_in_days(maxdays=90)) # get nobody's number of tweets in last 90 days 


