#Twitter Miner, Parser and Push to Solr
####Built by Aneesh Bhatnagar

The Twitter Miner, Parser and Push to Solr application consists of mainly 4 different scripts and a few additional scripts. It was written for a graduate course at University at Buffalo. The use of each of these scripts is listed below. 

* live_stream.py : This file makes use of the Twitter Streaming API and fetches tweets from the live stream as and when they come, based on the hashtags that you provide to the script. It stores them in files of 250 tweets per file, in JSON format.
* search.py : This files makes use of the Twitter Search API and fetches tweets based on various hashtags, language or date of tweet. It saves all the tweets in a single file.
* parsing.py : This file parses the fetched tweets by reading their JSON files and then getting the values required by the project. It also makes use of NLTK to remove stopwords from various languages and makes use of a specific file for korean stopwords since they are not present in NLTK.
* send_to_solr.py : This script basically sends all the tweets from the listed files or the directory to a Solr installation on any server. It can be modified to access any specific IP, port number or Solr installation.
* count_rt.py : This function reads all the files in a specific directory and counts the total number of tweets present and the total number of retweets in this folder. It was required for this project to calculate the number of retweets.
