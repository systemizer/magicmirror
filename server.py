import urllib
import markdown
import requests
import json
import tornado.web
import tornado.ioloop
from tornado import template, ioloop
from mwlib.uparser import simpleparse
from config import *
from lxml import etree
from utils import image_search, wikipedia_search, wolframalpha_search, freebase_search


loader = template.Loader("templates")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate())

class ImageHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        image = image_search(keyword)
        self.write(loader.load("image.html").generate(image_url=image['url']))

class WikipediaHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        self.write(wikipedia_search(keyword))

class WolframAlphaHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        results = wolframalpha_search(keyword)
        self.write(loader.load("wolframalpha.html").generate(results=results))

class FreebaseHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        desc,image_url = freebase_search(keyword)
        self.write(json.dumps({'description':desc,'image_url':image_url}))

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/resources/image/",ImageHandler),
    (r"/resources/wikipedia/", WikipediaHandler),
    (r"/resources/freebase/", FreebaseHandler),
    (r"/resources/wolframalpha/", WolframAlphaHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "static"}),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
