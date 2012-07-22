import random
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
from utils import *

options.logging='none'

loader = template.Loader("templates")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate(query_type=None))

class AudioHandler(tornado.web.RequestHandler):
    def post(self):        
        
		#print '_______________', self.request.files
		body = self.request.files['recording'][0]['body']
		query_type = self.get_argument("mode")

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

		query_types = ["Image","Web","Wikipedia","Analytical"]
		if query_type not in query_types:
		    query_type = query_types[random.randint(0,len(query_types))]

		if query_type=="Image":
		    background_size = "contain"
		    image = image_search(keyword)		
		    self.write(loader.load("image.html").generate(image_url=image['url'],background_size=background_size,query_type=query_type))
		elif query_type=="Web":
		    url = lucky_search(keyword)
		    self.write(loader.load("redirect.html").generate(url=url,query_type=query_type))
		elif query_type=="Wikipedia":
		    url = wikipedia_search(keyword)
		    self.write(loader.load("redirect.html").generate(url=url,query_type=query_type))
		elif query_type=="Analytical":
		    results,image_url,desc = wolframalpha_search(keyword)
		    self.write(loader.load("wolframalpha.html").generate(results=results,keyword=keyword,image_url=image_url,desc=desc,query_type=query_type))


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/audio/", AudioHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "static"}),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
