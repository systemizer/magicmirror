import urllib
import requests
import json
import tornado.web
import tornado.ioloop
from tornado import template, ioloop
from mwlib.uparser import simpleparse


loader = template.Loader("templates")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate())

# class WikipediaHandler(tornado.web.RequestHandler):
#     def get(self):
#         keyword = self.get_argument("keyword")

#         payload = {'format':'json',
#                    'action':'query',
#                    'titles':keyword,
#                    'prop':'revisions',
#                    'rvprop':'content'}        

#         base_url = "http://en.wikipedia.org/w/api.php"
#         url = "%s?%s" % (base_url,urllib.urlencode(payload))
#         r = requests.get(url)
#         self.write(simpleparse(unicode(r.json['query']['pages']['6710844']['revisions'][0]['*'])))

class FreebaseHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        payload1 = {'query':keyword}
        url1 = "%s?%s" % ("https://www.googleapis.com/freebase/v1/search",urllib.urlencode(payload1))

        r1 = requests.get(url1)
        mid = r1.json['result'][0]['mid']

        url2 = "https://www.googleapis.com/freebase/v1/text/%s" % mid
        r2 = requests.get(url2)        
        desc = r2.json['result']
        image_url = "https://www.googleapis.com/freebase/v1/image%s?&maxwidth=0&maxheight=0" % mid

        self.write(json.dumps({'description':desc,'image_url':image_url}))

application = tornado.web.Application([
    (r"/", MainHandler),
    #(r"/resources/wikipedia/", WikipediaHandler),
    (r"/resources/freebase/", FreebaseHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "static"}),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
