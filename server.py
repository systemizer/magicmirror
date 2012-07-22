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
from bs4 import BeautifulSoup


loader = template.Loader("templates")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("index.html").generate())

class ImageHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        base_url = "http://ajax.googleapis.com/ajax/services/search/images"
        payload = {'v':'1.0',
                   'rsz':'8',
                   'q':keyword,
                   'safe':'active'}

        url = "%s?%s" % (base_url,urllib.urlencode(payload))
        r = requests.get(url)
        images = r.json['responseData']['results']
        
        image = sorted(images,key= lambda x: -int(x['width']))[0]
        self.write(loader.load("image.html").generate(image_url=image['url']))

class WikipediaHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        payload1 = {'query':keyword}
        url1 = "%s?%s" % ("https://www.googleapis.com/freebase/v1/search",urllib.urlencode(payload1))

        r1 = requests.get(url1)
        results = r1.json['result']
        
        f_result = None

        for result in results:
            if result.has_key("id") and result['id'].startswith("/en/") and result.has_key("notable"):
                f_result = result
                break

        if not f_result:
            f.write("failed to find entity")

        url_path = f_result['id'].replace("/en/","")
        url = "http://en.wikipedia.org/wiki/%s" % url_path
        
        r2 = requests.get(url)
        self.write(r2.text)

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
#         pages = r.json['query']['pages']
#         self.write(r.json)
        
#         wikitext = pages[pages.keys()[0]]['revisions'][0]['*']
#         infobox_index = wikitext.index('{{Infobox')
#         if infobox_index==-1:
#             self.write("FAILED")
#         wikitext = wikitext[infobox_index:]
#         wikitext = wikitext[0:wikitext.index("}}")]
#         results = {}
#         for info_part in wikitext.split("|")[1:]:            
#             entry = info_part.split("=")
#             if len(entry)!=2:
#                 continue
#             results[entry[0]] = entry[1].replace("[","").replace("]","").replace("\n","")

#         self.write(json.dumps(results))


class WolframAlphaHandler(tornado.web.RequestHandler):
    def get(self):
        keyword = self.get_argument("keyword")
        base_url = "http://api.wolframalpha.com/v2/query"
        payload = {'input':keyword,
                   'appid':WOLFRAM_ALPHA_KEY}

        url = "%s?%s" % (base_url,urllib.urlencode(payload))
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        results = []
        for pod in soup.find_all("pod"):
            results.append({'title':pod['title'],
                            'plaintext':pod.find("plaintext").text,
                            'img_url':pod.find("img")['src']
                            })

        self.write(loader.load("wolframalpha.html").generate(results=results))

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
    (r"/resources/image/",ImageHandler),
    (r"/resources/wikipedia/", WikipediaHandler),
    (r"/resources/freebase/", FreebaseHandler),
    (r"/resources/wolframalpha/", WolframAlphaHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "static"}),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
