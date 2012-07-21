import urllib
import requests
import json
import tornado.web
import tornado.ioloop
from tornado import template, ioloop


loader = template.Loader("templates")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate())

class WikipediaHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")

        payload = {'format':'json',
                   'action':'query',
                   'titles':keyword,
                   'prop':'revisions',
                   'rvprop':'content'}        

        base_url = "http://en.wikipedia.org/w/api.php"
        url = "%s?%s" % (base_url,urllib.urlencode(payload))
        r = requests.get(url)
        self.write(r.json)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/resources/wikipedia/", WikipediaHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "static"}),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
