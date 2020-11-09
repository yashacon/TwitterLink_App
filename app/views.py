from django.shortcuts import render,redirect
import tweepy
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from .models import *
from django.db.models import Count
from decouple import config
from datetime import date, timedelta
import json

Consumer_Key=config('Consumer_Key')
Consumer_Secret=config('Consumer_Secret')
# Create your views here.

def api_obj(request):
	oauth = tweepy.OAuthHandler(Consumer_Key, Consumer_Secret)
	access_key = request.session['access_key_token']
	access_secret = request.session['access_secret_token']
	oauth.set_access_token(access_key, access_secret)
	api = tweepy.API(oauth, wait_on_rate_limit=True)
	return api

def login(request):
    if request.session.get('access_key_token',None) is not None :
        return redirect('Home')
    oauth=tweepy.OAuthHandler(Consumer_Key,Consumer_Secret)
    try:
        redirect_url = oauth.get_authorization_url(True)
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
    request.session['request_token']= oauth.request_token    
    return HttpResponseRedirect(redirect_url)

def callback(request):
    verifier = request.GET.get('oauth_verifier')
    oauth = tweepy.OAuthHandler(Consumer_Key, Consumer_Secret)
    token = request.session.get('request_token')
    request.session.delete('request_token')
    oauth.request_token = token
    try:
        oauth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')
    request.session['access_key_token']=oauth.access_token
    request.session['access_secret_token']= oauth.access_token_secret
    return redirect('Home')
    
def logout(request):
    if request.session.get('access_key_token',None) is not None :
        request.session.clear()
        logout(request)        
    return redirect('Homelogin')

def home(request):
    if request.session.get('access_key_token',None) is not None :
        api=api_obj(request)
        user=api.me()
        context={
            'username':user.name
        }
        return render(request, 'home.html', context)
    return redirect('Homelogin')

def homelogin(request):
    try:
        access_key=request.session.get('access_key_token',None)
        if access_key is None:
            return render(request,'homelogin.html')
    except KeyError:
        return render(request,'homelogin.html')
    return redirect('Home')

def all_twt(request):
    if request.session.get('access_key_token',None) is not None :
        api=api_obj(request)
        user=api.me()
        tweets=Tweets.objects.all()
        context={
            'my_list':tweets,
            'username':user.name
        }
        return render(request,'all_t.html',context)
    return redirect('Login')

def top_user(request):
    if request.session.get('access_key_token',None) is not None:
        tweets=Tweets.objects.values('User').order_by().annotate(user_count=Count('User'))
        if len(tweets)==0:
            api=api_obj(request)
            user=api.me()
            context={
                'username':user.name
            }
            return render(request,'top_user.html',context)
        Uid=max(tweets,key=lambda x:x['user_count'])
        api=api_obj(request)
        user=api.me()
        max_user=api.get_user(Uid['User'])
        context={
            'user':max_user,
            'username':user.name
        }
        return render(request,'top_user.html',context)
    return redirect('Login')

def top_domain(request):
    if request.session.get('access_key_token',None) is not None:
        tweets=Tweets.objects.values('Domain').order_by().annotate(domain_count=Count('Domain'))
        tweets=sorted(tweets,key=lambda x:x['domain_count'],reverse=True)
        api=api_obj(request)
        user=api.me()
        domains=[]
        for i in range(0,min(3,len(tweets))):
            domains.append([tweets[i]['Domain'],tweets[i]['domain_count']])
        context={
            'my_list':domains,
            'username':user.name
        }
        return render(request,'top_domain.html',context)
    return redirect('Login')


class save_data():
    def get_domain(self,str):
        for x in range(0, len(str)):
            if (str[x] == '/'):
                return str[0:x]

    def insert_db(self,ttweet, url):
        tweet = Tweets()
        tweet.id = str(ttweet.id) + str(ttweet.user.id)
        tweet.Name = ttweet.user.name
        tweet.User = ttweet.user.id
        tweet.Tweet_id = ttweet.id
        tweet.Text = ttweet.text
        tweet.Domain = self.get_domain(url[0]['display_url'])
        tweet.Display_picture = ttweet.user.profile_image_url
        tweet.save()

def link_twt(request):
    if request.session.get('access_key_token',None) is not None:
        api = api_obj(request)
        user = api.me()
        delta = date.today() - timedelta(days=7)
        my_list = []
        for tweet in tweepy.Cursor(api.home_timeline, since_id=delta).items(50):
            url = tweet.entities['urls']
            if len(url) != 0:
                if url[0]['display_url'][:7] != 'twitter':
                    my_list.append(tweet)
                    try:
                        save_data().insert_db(tweet, url)
                    except:
                        print('problem')
                        continue
        context={
            'my_list': my_list,
            'username': user.name
        }
        return render(request, 'link_t.html',context)
    return redirect('Login')  