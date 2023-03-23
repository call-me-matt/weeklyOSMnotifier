#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import mechanize => migrate to MechanicalSoup
import argparse
import collections
import os
import pprint
import smtplib
import time
import traceback
from copy import deepcopy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date
import xmlrpc.client
import re
import feedparser
import requests
import telepot
import tweepy
import yaml
from mastodon import Mastodon
from PIL import Image
import urllib.request

import logging

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(levelname)s] %(message)s"
    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class configResolver(object):
    def __init__(self, args):
        with open(os.path.join('configs','configs.yaml'),"r") as hiryaml:
            self.hierarchy_conf = yaml.full_load(hiryaml)
            self.configs = collections.OrderedDict()
            self.args = args
            dummy_conf = osmSPAM()
            dummy_conf.load_params(args)
            dummy_conf.crawl_latest_weekly()
            dummy_conf.load_image()
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
                    data = yaml.full_load(fstr)
                    if data is not None:
                        conf.load_from_config(data)
                if conf.runnable == True:
                        self.configs[(conf.context, conf.lang)] = conf
                if has_children:
                    self.stack.append(conf)
                    self.load_hierarchy(f[fkey])
                    self.stack.pop()
            else:
                logger.error("File not found:"+fname)

class osmSPAM(object):

    def __init__(self):
        """ key: """
        self.context  = ''  # context we are using (passed in as cli-parameter)
        self.lang     = ''  # language or list of languages
        """ cmd which can be overriden in file """
        self.do_forum     = False
        self.do_telegram  = False
        self.do_josm      = False
        self.do_mastodon  = False
        self.do_pin_mastodon   = False
        self.do_unpin_mastodon = False
        self.do_twitter   = False
        self.do_mail      = False
        self.do_show_pic  = False
        """ values from config """
        self.runnable = False # set this variable if the config can actually be called
        self.url = ''  # url that we are sending or tweeting
        self.mastodon_INSTANCE = ''
        self.mastodon_TOKEN = ''
        self.tw_CONSUMER_KEY = ''
        self.tw_CONSUMER_SECRET = ''
        self.tw_ACCESS_KEY = ''
        self.tw_ACCESS_SECRET = ''
        self.tw_text = ''
        self.pic = ''
        self.image = ''
        self.mail_user = ''
        self.mail_pw   = ''
        self.mail_smtp_port = 0
        self.mail_smtp_host = ''
        self.mail_subject = ''
        self.mail_subject = ''
        self.mail_from  = ''
        self.mail_to = []
        self.mail_body = ''
        self.forum_KEY = ''
        self.forum_to = []
        self.telegram_TOKEN     = ''
        self.telegram_to    = []
        self.josm_user = ''
        self.josm_pw = ''
        self.josm_body = ''
        """ derrived values """
        self.publishdate = []

    def load_params(self,args):
        self.pic = vars(args)['pic']
        self.do_show_pic = vars(args)['showpic']
        self.do_mail = vars(args)['mail']
        self.do_mastodon = vars(args)['mastodon']
        self.do_twitter = vars(args)['twitter']
        self.do_forum = vars(args)['forum']
        self.do_telegram = vars(args)['telegram']
        self.do_josm = vars(args)['josm']

    def crawl_latest_weekly(self):
        self.post_nr  = '' # wochennotiznr or weeklyosm nr
        self.url_no  = '' # wochennotiznr or weeklyosm nr
        self.date_from     = ''
        self.date_to       = ''
        self.daterange_str = ''

        feed_url = 'https://weeklyosm.eu/feed/'
        blog_feed = feedparser.parse(feed_url)

        blog_title = blog_feed.entries[0].title
        self.post_nr = re.search('weeklyOSM ([0-9]+)', blog_title).group(1)

        blog_link = blog_feed.entries[0].link
        self.url_no = blog_link.rsplit('/', 1)[1]

        blog_description = blog_feed.entries[0].description
        blogdate_fromto = re.search('([0-9]+/[0-9]+/[0-9]+)\-([0-9]+/[0-9]+/[0-9]+)', blog_description)
        self.date_from = blogdate_fromto.group(1)
        self.date_to = blogdate_fromto.group(2)

        if self.pic == 'auto':
            blog_content = blog_feed.entries[0].content
            self.pic = re.search('<img[^>]+src="(https://weeklyosm.eu/wp-content/uploads/[^"]+)', str(blog_content)).group(1)

        while True:
            print(f"* weeklyOSM post number: {self.post_nr}")
            print(f"* wordpress url number: {self.url_no}")
            print(f"* date from: {self.date_from}")
            print(f"* date to: {self.date_to}")
            print(f"* image path: {self.pic}")
            user_input = input('Confirm? [Y/n] ')
            if not user_input or user_input in ('Y','y'):
                break
            logger.warning ("Values not confirmed, please input manually")
            self.post_nr = input('weeklyOSM post number? ')
            self.url_no = input('wordpress url number? ')
            self.date_from = input('date from? ')
            self.date_to = input('date to? ')
            self.pic = input('image path? ')

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
                                'do_telegram',
                                'do_josm',
                                'do_mastodon',
                                'do_twitter',
                                'do_mail',
                                'do_show_pic',
                                'url',
                                'mastodon_INSTANCE',
                                'mastodon_TOKEN',
                                'do_pin_mastodon',
                                'do_unpin_mastodon',
                                'telegram_TOKEN',
                                'josm_user',
                                'josm_pw',
                                'josm_body',
                                'tw_CONSUMER_KEY',
                                'tw_CONSUMER_SECRET',
                                'tw_ACCESS_KEY',
                                'tw_ACCESS_SECRET',
                                'tw_text',
                                'pic',
                                'image',
                                'mail_user',
                                'mail_pw',
                                'mail_smtp_port',
                                'mail_smtp_host',
                                'mail_subject',
                                'mail_subject',
                                'mail_from',
                                'mail_to',
                                'mail_body',
                                'forum_KEY',
                                'forum_to',
                                'telegram_to']:
                    self.assign_safe(field,conf)

    def load_image(self):
        self.image = None
        if self.pic:
            try:
                if self.pic.startswith('http'):
                    img_download = urllib.request.urlretrieve(self.pic)
                    self.image = Image.open(img_download[0])
                elif os.path.isfile(self.pic):
                    self.image = Image.open(self.pic)
                else:
                    raise ValueError("image not found")
            except Exception as e:
                logger.error(e)
                exit(1)
            if self.do_show_pic:
                self.image.show()
                user_input = input('Confirm image? [Y/n] ')
                if user_input and user_input not in ('Y','y'):
                    logger.warning("User aborted for wrong image.")
                    exit()
                self.do_show_pic = False

    def set_date_str(self):
        self.daterange_str = self.date_from + '-' + self.date_to
        today = date.today()
        self.publishdate_iso = today.strftime("%Y-%m-%d")
        self.publishdate_slash = today.strftime("%d/%m/%Y")
        self.publishdate_dot = today.strftime("%d.%m.%Y")
        self.publishdate_dash = today.strftime("%d-%m-%Y")

    def create_texts(self):
        self.set_date_str()
        self.url = self.url.format(c=self)
        self.mail_body = self.mail_body.format(c=self)
        self.mail_subject = self.mail_subject.format(c=self)
        self.tw_text = self.tw_text.format(c=self)
        self.mail_from = self.mail_from.format(c=self)
        self.josm_body = self.josm_body.format(c=self)

    def check_url_exists(self):
        r = requests.get(self.url)
        return r.status_code == 200

    def send_email(self, recipient):  # dunno why the loop at this call and the list-handling inside - just leaving it as a param for paranoids
        TO = recipient if type(recipient) is list else [recipient]
        if not TO: return

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
            logger.info('successfully sent the mail to '+", ".join(TO))
        except:
            logger.error("failed to send mail")
            traceback.print_exc()
            pprint.pprint((self.mail_user, self.mail_pw,self.mail_from))
            
        return

    def post_forum(self, topicId):
        logger.info(f'...community forum post to https://community.openstreetmap.org/t/-/{topicId}.')

        try:
            FORUM_API = "https://community.openstreetmap.org/posts.json"

            data = {
                "title": self.mail_subject,
                "raw": self.mail_body,
                "topic_id": topicId,
                "category": 0,
                "target_recipients": "",
                "target_usernames": "",
                "archetype": "",
                "created_at": "",
                "embed_url": "",
                "external_id": ""
            }

            headers = {
                "Content-Type": "application/json",
                "User-Api-Key": self.forum_KEY,
                "Accept": "application/json"
            }

            response = requests.post(FORUM_API, json=data, headers=headers)

            logger.info(f"Status Code {response.status_code}")
            logger.debug(f"JSON Response: {response.json()}")

        except:
            logger.error("failed to publish")
            traceback.print_exc()

    def tweet(self):
        logger.info('...tweet...')

        auth = tweepy.OAuthHandler(self.tw_CONSUMER_KEY, self.tw_CONSUMER_SECRET)
        auth.set_access_token(self.tw_ACCESS_KEY, self.tw_ACCESS_SECRET)
        api = tweepy.API(auth)

        # update twitter status
        if self.pic:
            logger.debug('sending tweet with image')
            pic = api.media_upload(self.image)
            api.update_status(status=self.tw_text, media_ids = [pic.media_id_string] )
        else:
            api.update_status(status=self.tw_text)

        logger.debug(self.tw_text)

    def toot(self):
        logger.info('...toot...')

        # login
        mastodon = Mastodon(
            access_token = self.mastodon_TOKEN,
            api_base_url = self.mastodon_INSTANCE
        )
        media = None
        
        # upload picture if applicable
        if self.pic:
            logger.debug('sending toot with image')
            pic = mastodon.media_post(self.image)
            media = [pic.id]

        # toot!
        toot = mastodon.status_post(self.tw_text, language=self.lang, media_ids=media)
        logger.debug(f"{toot}")

        # pin status
        if self.do_pin_mastodon:
            try:
                if self.do_unpin_mastodon:
                    for pinned_toot in mastodon.account_statuses(mastodon.me().id, pinned=True):
                        logger.info(f"unpinning previous toot {pinned_toot.id}")
                        resp = mastodon.status_unpin(pinned_toot.id)
                        logger.debug(f"{resp}")
                resp = mastodon.status_pin(toot.id)
                logger.info(f"pinned toot")
                logger.debug(f"{resp}")
            except Exception as e:
                logger.error("failed to pin mastodon status:")
                logger.error (e)

    def telegram(self, bot, recipient):
        logger.info(f'...telegramming {recipient}...')
        try:
            resp = bot.sendMessage(int(recipient), self.tw_text)
            logger.info (resp)
        except Exception as e:
            logger.error (e)

        # pin message:
        # bot.unpinChatMessage(recipient) # unpins most recent chat message
        # bot.pinChatMessage(recipient,resp['message_id'],True)

    def post_josm(self):
        logger.info(f'...posting to josm...')
        with xmlrpc.client.ServerProxy(
            f"https://{self.josm_user}:{self.josm_pw}@josm.openstreetmap.de/login/xmlrpc"
        ) as server:
            try:
                wikipage = "StartupPageSource" # use "Sandbox" for testing
                wikicontent = server.wiki.getPage(wikipage)

                BEGINBLOCK = "# Begin weekly - leave at the top of the weeklyOSM section, automatically updated, do not edit manually"
                ENDBLOCK = "# End weekly - leave at the bottom of the weeklyOSM section, automatically updated, do not edit manually"
                BEGINNEWS = "# Begin news - leave at the top of the news section, do not edit or move this comment"

                newblock = f"{BEGINBLOCK}\n{self.josm_body}{ENDBLOCK}"

                logger.debug(newblock)

                blockpattern = re.compile(f"{BEGINBLOCK}.*?{ENDBLOCK}\n", flags=re.DOTALL)
                oldblock = blockpattern.search(wikicontent)
                if oldblock is None:
                    raise ValueError(
                        "Old weeklyOSM block not found in the wiki page. Check for magic strings in the source."
                    )
                oldblock = oldblock.group()

                if oldblock == newblock:
                    raise ValueError("The page is already up to date. No changes needed.")

                newcount = newblock.count("\n")
                oldcount = oldblock.count("\n") - 1
                if oldcount != newcount:
                    raise ValueError(
                        f"Number of old translations ({oldcount-3}) does not match new translation ({newcount-3}). Manually added translation? Manual edit?"
                    )

                # Drop the old weekly, insert new one at top
                wikicontent = wikicontent.replace(oldblock, "").replace(BEGINNEWS, f"{BEGINNEWS}\n{newblock}")
                server.wiki.putPage(
                    wikipage,
                    wikicontent,
                    {"comment": "Semi-automatic weeklyOSM update"},
                )
                logger.info("Update successful")
            except xmlrpc.client.ProtocolError as e:
                logger.error(f"An XML-RPC error occurred: {e}")
            except ValueError as e:
                logger.error(f"A validation error occurred: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")


    def send_stuff(self):
        self.create_texts()
        logger.info("Check if URL " + self.url + " exists before advertising...")
        if not self.check_url_exists():
            logger.error("URL " + self.url + " seems to be wrong")
            exit(1)

        if self.do_twitter:
            self.tweet()
        if self.do_mastodon:
            self.toot()
        if self.do_telegram:
            bot = telepot.Bot(self.telegram_TOKEN)
            for to in self.telegram_to:
                self.telegram(bot, to)
        if self.do_mail:
            for to in self.mail_to:
                self.send_email(to)
        if self.do_forum and self.forum_to:
            # only one message per language, as multiple posts with same text are rejected from forum
            self.post_forum(self.forum_to)
        if self.do_josm:
            self.post_josm()

        return

# create logger
logger = logging.getLogger("weeklyNotifier")
logger.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)  

argparser = argparse.ArgumentParser(prog='weekly2all',description='Python 3 script to notify about a new issue of Wochennotiz/weeklyOSM.', epilog='example: python weekly2all.py --mail --forum --twitter --mastodon --pic ~/downloads/1.jpg "WEEKLY" "en,de"')

argparser.add_argument('--twitter', action='store_true', help='send twitter notification')
argparser.add_argument('--mastodon', action='store_true', help='send mastodon notification')
argparser.add_argument('--mail',  action='store_true', help='send mail')
argparser.add_argument('--forum',  action='store_true', help='send post to forum threads')
argparser.add_argument('--telegram',  action='store_true', help='send announcements to telegram channels and groups where the bot is admin')
argparser.add_argument('--josm',  action='store_true', help='send announcements to josm wiki (shown at josm program start)')
argparser.add_argument('--pic', help='picture for mastodon and twitter, use auto to retrieve from latest weekly')
#argparser.add_argument('--pic', nargs='?', default=None, const='auto', help='picture for mastodon and twitter, use without filename to retrieve from latest weekly') # not working, https://github.com/python/cpython/issues/53584
argparser.add_argument('--showpic',  action='store_true', help='show picture before sending tweet/toot')
argparser.add_argument('ctxt',  help='context for sending')
argparser.add_argument('lang',  help='list of languages of context' )

args = argparser.parse_args()

logger.debug(args)

#argparser.print_help();
#pprint.pprint(vars(args))

cfr = configResolver(args)

for i, lang in enumerate(vars(args)['lang'].split(',')):
    logger.info (f"publishing {lang}...")

    config = cfr.configs.get((vars(args)['ctxt'], lang))
    if  not config:
        logger.error(f"Sorry no matching config for <{lang}>. Available:")
        logger.info(f"{cfr.configs.keys()}")
    else:
        config.create_texts()
        #pprint.pprint(vars(config))
        logger.debug(f"{config}")
        # only show picture for first iteration:
        if i: config.do_show_pic = False
        config.send_stuff()