import tornado.ioloop
import tornado.web
from tornado import template, options
import requests
import random
import envoy
import NaiveWordSelector
import json
import urllib
import markdown
import json
import tornado.web
from lxml import etree
from bs4 import BeautifulSoup
from tornado import template, ioloop
import markdown
import requests
import json
from utils import image_search, wikipedia_search, wolframalpha_search, freebase_search
import os


options.logging='none'

loader = template.Loader("templates")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class AudioHandler(tornado.web.RequestHandler):
    def post(self):

		#print '_______________', self.request.files
		body = self.request.files['recording'][0]['body']
	
		filename = str(int(random.random()*1000000))
		file = open('tempfiles/' + filename + '.wav', 'w')
		file.write(body)
		file.close()

		command = '/opt/sox-14.4.0/sox tempfiles/'+ filename + '.wav ' + 'tempfiles/' + filename + '.flac'
	#	print 'command: ', command

		r = envoy.run(command)
		if r.status_code != 0:
			print 'bad status code ', r.status_code


		url = 'http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium'
		headers={'Content-Type': 'audio/x-flac; rate=16000'}
		r = requests.post(url, 
				files={'eiffel.flac' : open('tempfiles/' + filename + '.flac' , 'rb')},
					headers=headers)

		#print r.json
		
		os.remove('tempfiles/' + filename + '.wav')
		os.remove('tempfiles/' + filename + '.flac')

		if r.status_code != 200 or r.json is None or not r.json['hypotheses']:
			self.write(json.dumps({'status': 'failed'}))
			return
		utterance = r.json['hypotheses'][0]['utterance']
		print utterance
		keyword = NaiveWordSelector.topKeyword(utterance.split(' '))
		print keyword


		payload1 = {'query':keyword}
		#url1 = "%s?%s" % ("https://www.googleapis.com/freebase/v1/search",urllib.urlencode(payload1))

		#r1 = requests.get(url1)
		#results = r1.json['result']

		#f_result = None

		#for result in results:
		#	if result.has_key("id") and result['id'].startswith("/en/") and result.has_key("notable"):
		#		f_result = result
		#		break

		#if not f_result:
		#	f.write("failed to find entity")

		#url_path = f_result['id'].replace("/en/","")
		#url = "http://en.wikipedia.org/wiki/%s" % url_path

		#r2 = requests.get(url)
		background_size = "contain"
		image = image_search(keyword)		
		self.write(loader.load("image.html").generate(image_url=image['url'],background_size=background_size))




application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/audio", AudioHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
