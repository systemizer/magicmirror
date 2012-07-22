import tornado.ioloop
import tornado.web
import memcache

kestrel = memcache.Client(['127.0.0.1:22133'])

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class AudioHandler(tornado.web.RequestHandler):
    def post(self):
    	print '_______________', self.request.files
    	kestrel.set('fileQ', self.request.files['eiffel.flac'][0]['body'])
        self.write("Hello, world")


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/audio", AudioHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()