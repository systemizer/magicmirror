from bs4 import BeautifulSoup as bs
import grequests
import logging
import sys
import requests
import simplejson as json
import logging

WORDNIK_ENDPOINT = ("http://api.wordnik.com//v4/word.json/","/frequency?startYear=2012&useCanonical=true")
WORDNIK_AUTH_KEY = "a7acd5e8c09b05c70c00705e15808bbe61a30408ce4dec62c"

COMMON_WORDS = {
    'yeah' : 100000,
    'but'  : 100000,
    'um'   : 100000,
    'uh'   : 100000,
    'something': 100000,
    'ok'    : 100000,
    'okay'  : 100000,
    'is'    : 100000,
    'it'    : 100000,
    'that'  : 100000,
    'that\'s' : 100000,
    'said' : 100000,
    'say'   : 100000,
    'much' : 100000,
    'yet'  : 100000,
    'cool' : 100000,
    'now' : 100000,
    'crap' : 100000,
    'what' : 100000,
    'when' : 100000,
    'of'    : 100000,
    'up'    : 100000,
    'for'   : 100000,
    'hi' : 100000,
    'there' : 100000,
    'fun' : 100000,
    'up' : 100000,
}

def topKeyword(words):
    words = [word.lower() for word in words]
    two_grams = []
    three_grams = []
    d = {}
    freqs = {}

    url = 'http://google.com/complete/search?output=toolbar'
    two_reqs = []
    three_reqs = []


    for word in words:
        if word in d:
            d[word][0]+=1
        elif word in COMMON_WORDS:
            d[word] = [1, COMMON_WORDS[word]]
        elif len(word) == 1:
            d[word] = [1, 100000]
        else:
            wordnik_url = WORDNIK_ENDPOINT[0]+word+WORDNIK_ENDPOINT[1]
            r = requests.get(wordnik_url, headers={'api_key': WORDNIK_AUTH_KEY}) 
            robj = json.loads(r.text)

            try:
                freq = sum([item["count"] for item in robj["frequency"]])+1 # add one to fix 0 freq results, which happen for the lowest freq valid words
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


######  three grams ######
    import urllib
    for index in range(0, len(words)-2):
       query = words[index] + ' ' + words[index + 1] + ' ' + words[index+2][0:1]
       print '3gram query ', query
       #print "%s?%s" % (url,urllib.urlencode({'q':query}))
       three_reqs.append(grequests.get(url, params={'q' : query}))

    three_responses = grequests.map(three_reqs, size = len(words))

    for i in range(len(three_responses)):
        xml = bs(three_responses[i].content)
        #print xml
        for sug in xml.find_all('suggestion'):
            s = sug['data']
            #print 'suggestion: ', s
            for gap1 in ('', ' '):
                for gap2 in ('', ' '):
                    new_q = words[i] + gap1 + words[i+1] + gap2 + words[i+2]
                    if new_q == s:
                        print 'data: ', s
                        three_grams.append(s)


    for phrase in three_grams:
        suitable = False
        for w in phrase.split(' '):
            if d[w][1] < 5:
                suitable = True
        if suitable:
            return phrase


######  two grams ######
    
    for index in range(0, len(words)-1):
        query = words[index] + ' ' + words[index + 1][0:1]
        print '2gram query ', query
        two_reqs.append(grequests.get(url, params={'q' : query}))
    

    two_responses = grequests.map(two_reqs, size = len(words))

    for i in range(len(two_responses)):
        xml = bs(two_responses[i].content)
        print xml
        for sug in xml.find_all('suggestion'):
            s = sug['data']
            #print 'suggestion: ', s
            if s == words[i] + '' + words[i+1] or s == words[i] + ' ' + words[i+1]:
                two_grams.append(s)


    for phrase in two_grams:
        suitable = False
        for w in phrase.split(' '):
            if d[w][1] < 10:
                suitable = True
        if suitable:
            return phrase

  
    return bestword


if __name__=="__main__":
    text = "The curiosity rover is going to land on mars on August 7th. The mars reconnaiscance orbiter will give us the first word of its fate, as the odyssey orbiter has had an unexpeced problem with a reaction wheel."
    words = text.split(" ")
    print topKeyword(words)
