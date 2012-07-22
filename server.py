import urllib
import markdown
import requests
import json
import tornado.web
import tornado.ioloop
from tornado import template, ioloop
from config import *
from utils import image_search, wikipedia_search, wolframalpha_search, freebase_search, lucky_search



loader = template.Loader("templates")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate())

class ImageHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        image = image_search(keyword)
        background_size = "contain"
        self.write(loader.load("image.html").generate(image_url=image['url'],background_size=background_size))

class LuckyHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        url = lucky_search(keyword)
        self.write(loader.load("redirect.html").generate(url=url))

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
    (r"/resources/lucky/",LuckyHandler),
    (r"/resources/wikipedia/", WikipediaHandler),
    (r"/resources/freebase/", FreebaseHandler),
    (r"/resources/wolframalpha/", WolframAlphaHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "static"}),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
