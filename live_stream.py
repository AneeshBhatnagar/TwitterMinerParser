import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
 
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)
count = 0
filecount = 1
filename = "iphone/iphone7-%s.json" % filecount

class MyListener(StreamListener):
    def on_data(self, data):
        try:
            with open(filename, 'a') as f:
                global count 
                global filename
                global filecount
                count = count + 1
                if (count == 250):
                	count = 0
                	filecount +=1
                	filename = "iphone/iphone7-%s.json" % filecount
                print count
                f.write(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        print(status)
        return True
 
twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(track=['#iPhone7', '#AppleEvent', '#AppleWatch2', '#iPhone7Plus', '#keynote'])
