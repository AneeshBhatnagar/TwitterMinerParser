# encoding=utf8  
# -*- coding: utf-8 -*-
import json
import glob
import re
import simplejson
from string import punctuation
import copy
from datetime import datetime
from nltk.corpus import stopwords
import pysolr
import sys

reload(sys)  
sys.setdefaultencoding('utf8')

special_symbols_pattern = re.compile(u'['
                                    u'\U0001F300-\U0001F64F'
                                    u'\U0001F680-\U0001F6FF'
                                    # u'\u2600-\u26FF\u2700-\u27BF'
                                    ']+', 
                                    re.UNICODE)

langs = ['en','es','tr','ko','fr','de','pt','it']
stop_words = {'en':stopwords.words("english"), "es":stopwords.words("spanish"), 
            "tr":stopwords.words("turkish"), 'ko':open("korean_stopwords.txt").read().split("\n"),
            "fr":stopwords.words("french"), "de":stopwords.words("german"),"pt":stopwords.words("portuguese"),
            "it":stopwords.words("italian")}

# kaomojis = {
#     "fishjump": "¸.·´¯`·.´¯`·.¸¸.·´¯`·.¸><(((º>", "headphones": "d(*_*)b", "bigheadphones": "O(*+*)O", "cthulhu": "^(;,;)^",
#     "wavedance": "(〜￣▽￣)〜", "wavedancerev": "〜(￣▽￣〜)", "sadblame": "(;´・`)>", "tantrum": "＼(｀0´)／", "crying": "(ू˃̣̣̣̣̣̣︿˂̣̣̣̣̣̣ ू)",
#     "yawn": "ᕙ(⇀‸↼‶)ᕗ", "dead": "╭( ✖_✖ )╮", "dancespin": "ヘ( ^o^)ノ＼(^_^ )", "boohoo": "(ू˃̣̣̣̣̣̣o˂̣̣̣̣̣̣ ू)⁼³₌₃", "rain": "⁝⁞⁝⁞ʕु•̫͡•ʔु☂⁝⁞⁝⁝",
#     "bow": "(シ_ _)シ", "cryexplain": "_:(´□`」 ∠):_", "nyam": "( ͒ ु- •̫̮ – ू ͒)", "dancegroup": "\(._.\) ƪ(‘-’ ƪ)(ʃ ‘-’)ʃ (/._.)/",
#     "dancesnap": "ヾ(-_- )ゞ", "yayjump": "o(〃＾▽＾〃)o", "chai": "( -_-)旦~", "food": "( ˘▽˘)っ♨", "party": "(º﹃º):.*೨", "hug": "(>^_^)><(^o^<)",
#     "hugkiss": "(づ￣ ³￣)づ", "meh": "ヽ(ー_ー )ノ", "fight": "Ｏ( ｀_´)乂(｀_´ )Ｏ", "stickup": "(҂‾ ▵‾)︻デ═一 \(˚▽˚’!)/", "yum": "(っ˘ڡ˘ς)",
#     "overhere": "〈(•ˇ‿ˇ•)-→", "saddream": "(  ु⁎ᴗ_ᴗ⁎)ु.｡oO", "wave": "ヾ(＾-＾)ノ", "zzz": "(-, – )…zzZZ"
# }
kaomojis = open("kaomojis.txt").read().split('\n')

output_file_name = 'parsed/tech.json'
f = open(output_file_name,'a')
file_count = 66
error = 0
topic = "tech"

count = 0

path = 'tech/*.json'
files = glob.glob(path)

for file in files:
    print file
    openfile = open(file, "r")
    lines = openfile.readlines()
    openfile.close()
    if count>6000:
        break
    for j in range(0,len(lines)):
        try:
            data = json.loads(lines[j])
            if data['text']:
                if data['text'].startswith("RT") == False:
                    continue  
        except:
            continue
        tweet_text = data['text']
        count+=1
        tweet_lang = ''
        list_hashtags = []
        list_mentions = []
        list_urls = []
        list_emoticons = []
        tweet_date = ''
        tweet_loc = ''

        text = data['text']
        number_hashtags =  len(data['entities']['hashtags'])
        for i in range (0,number_hashtags):
            list_hashtags.append(data['entities']['hashtags'][i]['text'])
            text = text.replace('#' + data['entities']['hashtags'][i]['text'],'')
        number_urls = len(data['entities']['urls'])
        for i in range (0,number_urls):
            list_urls.append(data['entities']['urls'][i]['url'])
            text = text.replace(data['entities']['urls'][i]['url'], '')
        number_mentions = len(data['entities']['user_mentions'])
        for i in range (0, number_mentions):
            list_mentions.append(data['entities']['user_mentions'][i]['screen_name'])
            text = text.replace('@'+data['entities']['user_mentions'][i]['screen_name'], '')
        try:
            number_media = len(data['entities']['media'])
            for i in range (0,number_media):
                list_urls.append(data['entities']['media'][i]['url'])
                text = text.replace(data['entities']['media'][i]['url'],'')
        except:
            error = error + 1
        #text = text.replace('RT ','')

        #Emojis and Emoticons
        list_emoticons = []
        list_emoticons.extend(special_symbols_pattern.findall(text))
        text = re.sub(special_symbols_pattern,' ',text)

        #Kaomojis
        for emo in kaomojis:
            list_emoticons.extend(re.findall(re.escape(emo),text))
            text = re.sub(re.escape(emo),' ',text)

        #Date
        try:
            tweet_date = datetime.fromtimestamp(int(data['timestamp_ms'])/1000).strftime("%Y-%m-%dT%H:00:00Z")
        except KeyError:
            tweet_date = datetime.strptime(re.sub(r"\+[0-9]{4} ","",data['created_at']),"%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%dT%H:00:00Z")

        #Geolocation
        if data['coordinates']:
            tweet_loc = ",".join([str(ja) for ja in data['coordinates']['coordinates'][::-1]])
        #Lang
        tweet_lang = data['lang']

        #Removing Punctuations
        punctuations = list('''!()-[]{};:'"\,<>./?@#$%^&*_~''')
        text = ''.join(ch for ch in text if ch not in punctuations + [u'\u201c',u'\u201d'])

        #StopWord Removal - Language Specific
        # eng_stopwords = ["a",'about','above','after','again','against','all','am','an','and','any','are',"aren't",'as','at','be','because','been','before','being','below','between','both','but','by',"can't",'cannot',"could","couldn't",'did',"didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from",'further','had',"hadn't",'has',"hasn't",'have',"haven't","having","he","he'd","he'll","he's","her","here","here's",'hers','herself','him','himself','his','how',"how's",'i',"i'd","i'll","i'm","i've","if","in",'into',"is","isn't",'it',"it's",'its','itself',"let's",'me',"more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"]
        # es_stopwords = ['un', 'una', 'unas', 'unos', 'uno', 'sobre', 'todo', 'tras', 'otro', 'alguno', 'alguna', 'algunos', 'algunas', 'ser', 'es', 'soy', 'eres', 'somos', 'sois', 'estoy', 'esta', 'estamos', 'estais', 'estan', 'como', 'en', 'para', 'atras', 'porque', 'estado', 'estaba', 'ante', 'antes', 'siendo', 'ambos', 'pero', 'por', 'poder', 'puede', 'puedo', 'podemos', 'podeis', 'pueden', 'fui', 'fue', 'fuimos', 'fueron', 'hacer', 'hago', 'hace', 'hacemos', 'haceis', 'hacen', 'cada', 'fin', 'incluso', 'conseguir', 'consigo', 'consigue', 'consigues', 'conseguimos', 'consiguen', 'ir', 'voy', 'va', 'vamos', 'vais', 'van', 'vaya', 'gueno', 'ha', 'tener', 'tengo', 'tiene', 'tenemos', 'teneis', 'tienen', 'el', 'la', 'lo', 'las', 'los', 'su', 'aqui', 'mio', 'tuyo', 'ellos', 'ellas', 'nos', 'nosotros', 'vosotros', 'vosotras', 'si', 'dentro', 'solo', 'solamente', 'saber', 'sabes', 'sabe', 'sabemos', 'sabeis', 'saben', 'ultimo', 'largo', 'bastante', 'haces', 'muchos', 'aquellos', 'aquellas', 'sus', 'entonces', 'tiempo', 'verdad', 'verdadero', 'ciertos', 'cierta', 'ciertas', 'intentar', 'intento', 'intenta', 'intentas', 'intentamos', 'intentais', 'intentan', 'dos', 'bajo', 'arriba', 'encima', 'usar', 'uso', 'usas', 'usa', 'usamos', 'usais', 'usan', 'emplear', 'empleo', 'empleas', 'emplean', 'ampleamos', 'empleais', 'valor', 'muy', 'era', 'eras', 'eramos', 'eran', 'modo', 'bien', 'cual', 'cuando', 'donde', 'mientras', 'quien', 'con', 'entre', 'sin', 'trabajo', 'trabajar', 'trabajas', 'trabaja', 'trabajamos', 'trabajais', 'trabajan', 'podria', 'podrias', 'podriamos', 'podrian', 'podriais', 'yo', 'aquel']
        
        if tweet_lang in langs:
            for word in stop_words[tweet_lang]:
                text = text.lower().replace(' ' + word +' ',' ')



        #Remove Spaces
        text = ' '.join(text.split())

        #Preparing Final JSON Object for Pushing
        tweet = {}

        tweet['topic'] = topic
        tweet['tweet_text'] = tweet_text
        tweet['text_%s'%tweet_lang] = text
        tweet['tweet_lang'] = tweet_lang
        tweet['hashtags'] = list_hashtags
        tweet['mentions'] = list_mentions
        tweet['tweet_urls'] = list_urls
        tweet['tweet_emoticons'] = list_emoticons
        tweet['tweet_date'] = tweet_date
        tweet['tweet_loc'] = tweet_loc

        #print json.dumps(tweet)
        f.write(json.dumps(tweet) + "\n")
f.close()