import json

total_files = 7
global number_tweets
global number_rt
global error
number_tweets = 0
number_rt = 0
error = 0

for i in range (1,total_files+1):
	file_name = "folder/files-%d.json" % i
	with open(file_name) as f:
		lines = f.readlines()
		number_tweets = number_tweets + len(lines)
		for j in range (0,len(lines)):
			data = json.loads(lines[j])
			try:
				if data['text'].startswith('RT') == True:
					number_rt = number_rt + 1
			except:
				error = error + 1
print "Total Number of Tweets:" + number_tweets - error
print "Total Number of RTs:" + number_rt
print "Total Number of Error Tweets:" + error