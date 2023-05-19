#NLP Assignment 2

#Harith Izani 1821037
#Muhammad Hariz Bin Hasnan 1827929
#Mohamad Arif Daniel Bin Muhamaddun 1917027
#Nur Atiqah binti Hasbullah 1920744

import re
import tweepy
import os
from tweepy import OAuthHandler
from textblob import TextBlob
from nltk.tokenize import word_tokenize

path = os.getcwd()
os.chdir(path)
  
class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'uUIUfdcmUGaWWRAN2wXv1RbB3'
        consumer_secret = '4WZFMohO00wsiuO4MeFIZ3PRh7tKU3YTWgoMWSVyA08nG0Xo0Y'
        access_token = '1181550179612123136-n9u0os6dZVm3gQcL1qmQGm5AJsssbN'
        access_token_secret = 'PpjUq1YyywVe46Qs2Rbz2LWhcdt6sJDBN59WBoR3S7Gjd'
  
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
  
    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
  
    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
  
    def get_tweets(self, query, count = 10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
  
        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search_tweets(q = query, geocode = "4.2105,101.9758,200km" ,count = count)
  
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
  
                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
  
                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
  
            # return parsed tweets
            return tweets
  
        except tweepy.TweepyException as e:
            # print error (if any)
            print("Error : " + str(e))

#Extracting all positive, negative and booster words from data files
def word_extract():
    positive_words = []
    negative_words = []
    negation_words = []
    booster_inc = []
    booster_dec = []
    
    with open('data files/positive.txt') as positive:
        positive_words = positive.readlines()
        positive_words = [line.rstrip() for line in positive_words]
    with open('data files/negative.txt') as negative:
        negative_words = negative.readlines()
        negative_words = [line.rstrip() for line in negative_words]
    with open('data files/negation.txt') as negation:
        negation_words = negation.readlines()
        negation_words = [line.rstrip() for line in negation_words]
    with open('data files/booster_inc.txt') as booster_inc:
        booster_inc = booster_inc.readlines()
        booster_inc = [line.rstrip() for line in booster_inc]
    with open('data files/booster_decr.txt') as booster_dec:
        booster_dec = booster_dec.readlines()
        booster_dec = [line.rstrip() for line in booster_dec]

    return positive_words,negative_words,negation_words,booster_inc,booster_dec

#Scoring each tweet based on the frequency of words found as well as booster words
def word_scorer(text,positive_words,negative_words,negation_words,booster_inc,booster_dec):
    score = 0
    #text_temp = word_tokenize(clean_tweet(text['text']))
    text_temp = word_tokenize(text['text'])
    for word in text_temp:
        current_sentiment = None
        for check_p in positive_words:
            if word == check_p: score += 1
            current_sentiment = 1
        for check_n in negative_words:
            if word == check_n: score -= 1
            current_sentiment = -1
        if text_temp.index(word) != 0:
            for check_o in negation_words: #Negation words will negate score of the word it is negating(amazing will +1 but if sentence says not amaazing then its overall neutral)
                if word == check_o:
                    if current_sentiment == 1: score -= 1
                    if current_sentiment == -1: score += 1
            for check_inc in booster_inc: #It will boost the score of the word it is boosting(if positive word then it will boost positively etc)
                if word == check_inc:
                    if current_sentiment == 1: score += 2
                    if current_sentiment == -1: score -= 2 
            for check_dec in booster_dec: #It will decrease the effetiveness of the word it is boosting(amazing will +1 but if it sentence says slighty amazing then the sentiment will be decreased by 0.5 etc) 
                if word == check_dec:
                    if current_sentiment == 1: score -= 0.5
                    if current_sentiment == -1: score += 0.5

    return score

hashtags = ['foodprice','foodcrisis','foodshortage','foodsecurity','priceincrease','foodinflation']
  
def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = []
    for hasht in hashtags:
        tweets.extend(api.get_tweets(query = hasht, count = 200))
  
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} % \
        ".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)))
  
    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'])
  
    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'])

    positive_words,negative_words,negation_words,booster_inc,booster_dec = word_extract()
    for tweet in tweets:
        tweet['score'] = word_scorer(tweet,positive_words,negative_words,negation_words,booster_inc,booster_dec)

    print('\n', 'ALL TWEETS WITH ITS RESPECTIVE SCORES\n')
    for tweet in tweets:
        print(tweet['text'],' ',tweet['score'])
  
if __name__ == "__main__":
    # calling main function
    main()
