from bs4 import BeautifulSoup as bs
import grequests
import logging
import sys

WORDNIK_ENDPOINT = ("http://api.wordnik.com//v4/word.json/","/frequency?startYear=2012&useCanonical=true")
WORDNIK_AUTH_KEY = "a7acd5e8c09b05c70c00705e15808bbe61a30408ce4dec62c"

import requests
import simplejson as json

import logging


def write(text):
    f = open('/Users/arashd/workspace/magicmirror/log.txt', 'w')
    f.write(text)
    f.flush()
    f.close()

def topKeyword(words):
    words = [word.lower() for word in words]
    two_grams = []
    d = {}

    url = 'http://google.com/complete/search?output=toolbar'
    reqs = []

    for index in range(0, len(words)-1):
        query = words[index] + ' ' + words[index + 1][0:-1]
        print '2gram query ', query
        reqs.append(grequests.get(url, params={'q' : query}))
    
    responses = grequests.map(reqs, size=len(words))

    for i in range(len(responses)):
        xml = bs(responses[i].content)
        for sug in xml.find_all('suggestion'):
            print 'suggestion: ', sug
            if sug['data'] == words[i] + ' ' + words[i+1]:
                print 'data: ', sug['data']
                two_grams.append(sug['data'])


    for word in words: 
        if word in d:
            d[word][0]+=1
        else:
            url = WORDNIK_ENDPOINT[0]+word+WORDNIK_ENDPOINT[1]
            r = requests.get(url, headers={'api_key': WORDNIK_AUTH_KEY}) 
            robj = json.loads(r.text)

            try:
                freq = robj["frequency"][0]["count"]+1 # add one to fix 0 freq results, which happen for the lowest freq valid words
            except:
                freq = 10

            d[word] = [1,freq]

    bestscore=0
    for word in d:
        count,langFreq = d[word]
        score = count * 1 / float(langFreq**3)
 #        print word,count,langFreq,score
        if score > bestscore:
            bestword = word
            bestscore = score
     
    if two_grams:
        return two_grams[0]
    return bestword



if __name__=="__main__":
    text = "The curiosity rover is going to land on mars on August 7th. The mars reconnaiscance orbiter will give us the first word of its fate, as the odyssey orbiter has had an unexpeced problem with a reaction wheel."
    words = text.split(" ")
    print topKeyword(words)
