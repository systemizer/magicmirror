import requests
import urllib
from bs4 import BeautifulSoup
from config import WOLFRAM_ALPHA_KEY

def image_search(keyword):
    base_url = "http://ajax.googleapis.com/ajax/services/search/images"
    payload = {'v':'1.0',
               'rsz':'8',
               'q':keyword,
               'safe':'active'}
    
    url = "%s?%s" % (base_url,urllib.urlencode(payload))
    r = requests.get(url)
    images = r.json['responseData']['results']        
    return sorted(images,key= lambda x: -int(x['width']))[0]

def wikipedia_search(keyword):
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
        return None
    
    url_path = f_result['id'].replace("/en/","")
    url = "http://en.wikipedia.org/wiki/%s" % url_path
    r2 = requests.get(url)
    return r2.text

def wolframalpha_search(keyword):
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
    return results

def freebase_search(keyword):
    payload1 = {'query':keyword}
    url1 = "%s?%s" % ("https://www.googleapis.com/freebase/v1/search",urllib.urlencode(payload1))

    r1 = requests.get(url1)
    mid = r1.json['result'][0]['mid']

    url2 = "https://www.googleapis.com/freebase/v1/text/%s" % mid
    r2 = requests.get(url2)        
    desc = r2.json['result']
    return desc,"https://www.googleapis.com/freebase/v1/image%s?&maxwidth=0&maxheight=0" % mid
