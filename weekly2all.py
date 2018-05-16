#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import mechanize => migrate to MechanicalSoup
import mechanicalsoup
import requests, time, tweepy, sys
import smtplib
import pprint
import argparse
from email.mime.text import MIMEText 
from copy import deepcopy
from PIL import Image
import time
import os
import collections
import yaml 



class configResolver(object):
    def __init__(self, args):
        with open(os.path.join('configs','configs.yaml'),"r") as hiryaml:
            self.hierarchy_conf = yaml.load(hiryaml)
            self.configs = collections.OrderedDict()
            self.args = args
            dummy_conf = osmSPAM()
            dummy_conf.load_params(args)
            self.stack = list()
            self.stack.append(dummy_conf)
            self.load_hierarchy(self.hierarchy_conf)

    def load_hierarchy(self,processlist):
        for f in processlist:
            has_children = isinstance(f,dict) 
            if has_children:
                fkey = list(f.keys())[0]
                fname = os.path.join('configs',fkey)
            else:
                fname = os.path.join('configs',f)

            if os.path.isfile(fname) == True:
                conf = deepcopy(self.stack[-1:][0])
                with open(fname,"r") as fstr:
                    data = yaml.load(fstr)
                    if data is not None:
                        conf.load_from_config(data)
                if conf.runnable == True:
                        self.configs[(conf.context, conf.lang)] = conf
                if has_children:
                    self.stack.append(conf)
                    self.load_hierarchy(f[fkey])
                    self.stack.pop()
            else:
                print("File not found:"+fname)
        
            


class osmSPAM(object):

    def __init__(self):
        """ key: """
        self.context  = ''  # context we are using (passed in as cli-parameter)
        self.lang     = ''  # language
        """ cmd Params: """
        self.post_nr  = '' # wochennotiznr or weeklyosm nr
        self.url_no  = '' # wochennotiznr or weeklyosm nr
        self.year          = ''
        self.month         = ''
        self.date_from     = ''
        self.date_to       = ''
        self.daterange_str = ''
        """ cmd which can be overriden in file """
        self.do_forum    = False
        self.do_twitter  = False
        self.do_mail     = False
        self.do_show_pic = False
        """ values from config """
        self.runnable = False # set this variable if the config can actually be called
        self.url = ''  # url that we are sending or tweeting
        self.forum_usr = ''
        self.forum_pw = ''
        self.forum_login_url = ''
        self.forum_urls = []
        self.tw_CONSUMER_KEY = ''
        self.tw_CONSUMER_SECRET = ''
        self.tw_ACCESS_KEY = ''
        self.tw_ACCESS_SECRET = ''
        self.tw_text          = ''
        self.tw_pic          = ''
        self.mail_user = ''
        self.mail_pw   = ''
        self.mail_smtp_port = 0
        self.mail_smtp_host = ''
        self.mail_subject = ''
        self.mail_subject     = ''
        self.mail_from     = ''
        self.mail_to    = []
        self.mail_body          = ''

    def load_params(self,args):
        self.post_nr = vars(args)['post']
        self.url_nr = vars(args)['url_no']
        self.year = vars(args)['year']
        self.month = vars(args)['month']
        self.date_from = vars(args)['dfrom']
        self.date_to = vars(args)['dto']
        self.tw_pic = vars(args)['twpic']
        self.do_show_pic = vars(args)['showpic']
        self.do_mail = vars(args)['mail']
        self.do_twitter = vars(args)['twitter']

    def assign_safe(self,name,conf):
        if name in conf:
            setattr(self,name,conf[name])

    def load_from_config(self,conf):
        if conf is not None:
            if isinstance(conf, dict):
                for field in  [ 'context',
                                'lang',
                                'runnable',
                                'do_forum',
                                'do_twitter',
                                'do_mail',
                                'do_show_pic',
                                'url',
                                'forum_usr',
                                'forum_pw',
                                'forum_login_url',
                                'forum_urls',
                                'tw_CONSUMER_KEY',
                                'tw_CONSUMER_SECRET',
                                'tw_ACCESS_KEY',
                                'tw_ACCESS_SECRET',
                                'tw_text',
                                'tw_pic',
                                'mail_user',
                                'mail_pw',
                                'mail_smtp_port',
                                'mail_smtp_host',
                                'mail_subject',
                                'mail_subject',
                                'mail_from',
                                'mail_to',
                                'mail_body' ]:
                    self.assign_safe(field,conf)
                    
    def set_date_str(self):
        self.daterange_str = self.date_from + '-' + self.date_to

    def create_texts(self):
        self.set_date_str()
        self.url = self.url.format(c=self)
        self.mail_body = self.mail_body.format(c=self)
        self.mail_subject = self.mail_subject.format(c=self)
        self.tw_text = self.tw_text.format(c=self)
        self.mail_from = self.mail_from.format(c=self)

    def check_url_exists(self):
        r = requests.get(self.url)
        return r.status_code == 200

    def send_email(self, recipient):  # dunno why the loop at this call and the list-handling inside - just leaving it as a param for paranoids
        if not self.do_mail:
            return

        TO = recipient if type(recipient) is list else [recipient]

        # Prepare actual message
        msg = MIMEText(self.mail_body, 'plain', 'UTF-8')
        msg['From'] = self.mail_from
        msg['To'] = ", ".join(TO)
        msg['Subject'] = self.mail_subject
        #pprint.pprint((self.mail_user, self.mail_pw,self.mail_from, TO, msg.as_string()))

        try:
            server = smtplib.SMTP(self.mail_smtp_host, self.mail_smtp_port)
            server.ehlo()
            server.starttls()
            server.login(self.mail_user, self.mail_pw)
            server.sendmail(self.mail_from, TO, msg.as_string())
            server.close()
            print('successfully sent the mail')
        except:
            print("failed to send mail")

        return

    def post_forum(self):

        if not self.do_forum:
            return
        print('...einloggen forum.openstreetmap.org...')
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(self.forum_login_url)
        browser.select_form(nr = 0)
        browser.form['req_username'] = self.forum_usr
        browser.form['req_password'] = self.forum_pw
        browser.submit_selected()
        print(self.mail_subject)
        print(self.mail_body)
        for i, url in enumerate(self.forum_urls):
            browser.open(url)
            browser.select_form(nr = 0)
            browser.form['req_subject'] = self.mail_subject
            browser.form['req_message'] = self.mail_body
            browser.submit_selected()
            if i != len(self.forum_urls) - 1:
                print('sleeping...')
                time.sleep(130)

    def tweet(self):
        if not self.do_twitter:
            return
        print('...tweet...')


        auth = tweepy.OAuthHandler(self.tw_CONSUMER_KEY, self.tw_CONSUMER_SECRET)
        auth.set_access_token(self.tw_ACCESS_KEY, self.tw_ACCESS_SECRET)
        api = tweepy.API(auth)
        
        if self.tw_pic:
            if os.path.isfile(self.tw_pic):
                img = Image.open(self.tw_pic)
                if self.do_show_pic:
                    img.show()
                    for i in range(10, 0, -1):
                        print('sending tweet with image in', i)
                        time.sleep(1)
                print('sending tweet with image')
                pic = api.media_upload(self.tw_pic)
                pprint.pprint(api.update_status(status=self.tw_text, media_ids = [pic.media_id_string] ))                
            else:
                print('image not found!')
                exit(1)
        else:
            api.update_status(status=self.tw_text)

        
        

        print(self.tw_text)

    def send_stuff(self):
        self.create_texts()
        print("Check if URL " + self.url + " exists before advertising...")
        if not self.check_url_exists():
            print("URL " + self.url + " seems to be wrong")
            exit(1)

        self.post_forum()
        self.tweet()
        for to in self.mail_to:
            self.send_email(to)

        return


argparser = argparse.ArgumentParser(prog='weekly2all',description='Python 2 script to notify about a new issue of Wochennotiz/weeklyOSM.', epilog='example: python weekly2all.py --twitter --mail "WEEKLY" "es" "311" "7831" "2016" "02" "23.02.2016" "29.02.2016"')


argparser.add_argument('--twitter', action='store_true', help='send twitter notification')
argparser.add_argument('--mail',  action='store_true', help='send mail')
argparser.add_argument('--twpic',  help='twitterpicture')
argparser.add_argument('--showpic',  action='store_true', help='show twitter picture')
argparser.add_argument('ctxt',  help='context for sending')
argparser.add_argument('lang',  help='language of context' )
argparser.add_argument('post',  help='post number')
argparser.add_argument('url_no',  help='url number')
argparser.add_argument('year',  help='year')
argparser.add_argument('month',  help='month')
argparser.add_argument('dfrom',  help='date from')
argparser.add_argument('dto',  help='date to')

args = argparser.parse_args()
#argparser.print_help();
#pprint.pprint(vars(args))

cfr = configResolver(args)

config = cfr.configs.get((vars(args)['ctxt'], vars(args)['lang']))
if  not config:
    print("Sorry no matching configs:")
    pprint.pprint(cfr.configs.keys())    
else:
    config.create_texts()
    pprint.pprint(vars(config))
    config.send_stuff()