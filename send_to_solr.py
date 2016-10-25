import json
import pysolr
import sys
import glob

address = '' #Along with Port Number
core_name = ''
solr = pysolr.Solr('http://%s/solr/%s'%(address,core_name), timeout=10)

count = 0
tweet_list = []
path = '/home/aneesh/twitterFetch/data-to-push/*.json'
files = glob.glob(path)
langs = ['en','es','tr','ko','fr','de','pt','it']
for file in files:
	with open(file) as f:
		data = f.readlines()
		for line in data:
			tweet = json.loads(line)
			if tweet['tweet_lang'] in langs:
				length = len(tweet['tweet_date']) -6
				tweet['tweet_date'] = tweet['tweet_date'][0:length] + '00:00Z'
				tweet_list.append(tweet)
				count +=1
			if len(tweet_list) % 10 == 0:
				solr.add(tweet_list)
				tweet_list = []
				print "Tweets uploaded ", count