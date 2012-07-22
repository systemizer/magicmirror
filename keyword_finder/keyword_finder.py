import memcache
import requests
import random
import envoy
import NaiveWordSelector


kestrel = memcache.Client(['127.0.0.1:22133'])

while True:
	next_file = kestrel.get('fileQ')
	if not next_file:
		continue
	filename = str(int(random.random()*1000000))
	file = open('tempfiles/' + filename + '.wav', 'w')
	file.write(next_file)
	file.close()

#	command = '/opt/sox-14.4.0/sox tempfiles/'+ filename + '.wav ' + 'tempfiles/' + filename + '.flac'
#	print 'command: ', command

	r = envoy.run(command)
	if r.status_code != 0:
		print 'bad status code ', r.status_code
		continue

	url = 'http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium'
	headers={'Content-Type': 'audio/x-flac; rate=16000'}
	r = requests.post(url, 
			files={'eiffel.flac' : open('tempfiles/' + filename + '.flac' , 'rb')},
				headers=headers)

#	print r.json
	
	if not hypotheses:
		self.write('status' : 'none found')
	utterance = r.json['hypotheses'][0]['utterance']
	keyword = NaiveWordSelector.topKeyword(utterance.split(' '))
	print keyword



