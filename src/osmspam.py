import os
from datetime import date
import re
import feedparser
import requests
import asyncio
from PIL import Image
import urllib.request

from connectors import (
    bluesky,
    forum,
    josm,
    lemmy,
    mail,
    mastodon,
    matrix,
    telegram,
    twitter,
)


class osmSPAM(object):

    def __init__(self, logger):
        """key:"""
        self.logger = logger
        self.context = ""  # context we are using (passed in as cli-parameter)
        self.lang = ""  # language or list of languages
        """ cmd which can be overriden in file """
        self.do_bluesky = False
        self.do_forum = False
        self.do_josm = False
        self.do_lemmy = False
        self.do_mail = False
        self.do_mastodon = False
        self.do_matrix = False
        self.do_telegram = False
        self.do_twitter = False
        """ values from config """
        self.runnable = False  # set this variable if the config can actually be called
        self.url = ""  # url that we are sending or tweeting
        self.pic = ""
        self.do_show_pic = False

        self.bluesky_text = ""
        self.bluesky_TOKEN = ""
        self.bluesky_USER = ""
        self.do_pin_mastodon = False
        self.do_unpin_mastodon = False
        self.forum_KEY = ""
        self.forum_to = []
        self.josm_body = ""
        self.josm_PW = ""
        self.josm_USER = ""
        self.lemmy_PW = ""
        self.lemmy_USER = ""
        self.mail_body = ""
        self.mail_from = ""
        self.mail_PW = ""
        self.mail_smtp_host = ""
        self.mail_smtp_port = 0
        self.mail_subject = ""
        self.mail_subject = ""
        self.mail_to = []
        self.mail_USER = ""
        self.mastodon_INSTANCE = ""
        self.mastodon_to = []
        self.mastodon_TOKEN = ""
        self.matrix_BASE = ""
        self.matrix_to = []
        self.matrix_TOKEN = ""
        self.matrix_USER = ""
        self.telegram_to = []
        self.telegram_TOKEN = ""
        self.tw_ACCESS_KEY = ""
        self.tw_ACCESS_SECRET = ""
        self.tw_CONSUMER_KEY = ""
        self.tw_CONSUMER_SECRET = ""
        self.tw_text = ""

        """ derrived values """
        self.publishdate = []

    def load_params(self, args):
        self.pic = vars(args)["pic"]
        self.do_show_pic = vars(args)["showpic"]
        self.do_bluesky = vars(args)["bluesky"]
        self.do_forum = vars(args)["forum"]
        self.do_josm = vars(args)["josm"]
        self.do_lemmy = vars(args)["lemmy"]
        self.do_mail = vars(args)["mail"]
        self.do_mastodon = vars(args)["mastodon"]
        self.do_matrix = vars(args)["matrix"]
        self.do_telegram = vars(args)["telegram"]
        self.do_twitter = vars(args)["twitter"]

    def crawl_latest_weekly(self):
        self.post_nr = ""  # wochennotiznr or weeklyosm nr
        self.url_nr = ""  # wochennotiznr or weeklyosm nr
        self.date_from = ""
        self.date_to = ""
        self.daterange_str = ""

        feed_url = "https://weeklyosm.eu/en/feed/"
        blog_feed = feedparser.parse(feed_url)

        blog_title = blog_feed.entries[0].title
        self.post_nr = re.search("weeklyOSM ([0-9]+)", blog_title).group(1)

        blog_link = blog_feed.entries[0].link
        self.url_nr = blog_link.rsplit("/", 1)[1]

        blog_description = blog_feed.entries[0].description
        blogdate_fromto = re.search(
            "([0-9]+/[0-9]+/[0-9]+)-([0-9]+/[0-9]+/[0-9]+)", blog_description
        )
        self.date_from = blogdate_fromto.group(1)
        self.date_to = blogdate_fromto.group(2)

        if self.pic == "auto":
            blog_content = blog_feed.entries[0].content
            self.pic = re.search(
                '<img[^>]+src="(https://weeklyosm.eu/wp-content/uploads/[^"]+)',
                str(blog_content),
            ).group(1)

        while True:
            print(f"* weeklyOSM post number: {self.post_nr}")
            print(f"* wordpress url number: {self.url_nr}")
            print(f"* date from: {self.date_from}")
            print(f"* date to: {self.date_to}")
            print(f"* image path: {self.pic}")
            user_input = input("Confirm? [Y/n] ")
            if not user_input or user_input in ("Y", "y"):
                break
            self.logger.warning("Values not confirmed, please input manually")
            self.post_nr = input("weeklyOSM post number? ")
            self.url_nr = input("wordpress url number? ")
            self.date_from = input("date from? ")
            self.date_to = input("date to? ")
            self.pic = input("image path? ")

    def assign_safe(self, name, conf):
        if name in conf:
            setattr(self, name, conf[name])

    def load_from_config(self, conf):
        if conf is not None:
            if isinstance(conf, dict):
                for field in [
                    "bluesky_text",
                    "bluesky_TOKEN",
                    "bluesky_USER",
                    "context",
                    "do_bluesky",
                    "do_forum",
                    "do_josm",
                    "do_lemmy",
                    "do_mail",
                    "do_mastodon",
                    "do_matrix",
                    "do_pin_mastodon",
                    "do_show_pic",
                    "do_telegram",
                    "do_twitter",
                    "do_unpin_mastodon",
                    "forum_KEY",
                    "forum_to",
                    "image",
                    "josm_body",
                    "josm_PW",
                    "josm_USER",
                    "lang",
                    "lemmy_PW",
                    "lemmy_USER",
                    "mail_body",
                    "mail_from",
                    "mail_PW",
                    "mail_smtp_host",
                    "mail_smtp_port",
                    "mail_subject",
                    "mail_subject",
                    "mail_to",
                    "mail_USER",
                    "mastodon_INSTANCE",
                    "mastodon_to",
                    "mastodon_TOKEN",
                    "matrix_BASE",
                    "matrix_to",
                    "matrix_TOKEN",
                    "matrix_USER",
                    "pic",
                    "runnable",
                    "telegram_to",
                    "telegram_TOKEN",
                    "tw_ACCESS_KEY",
                    "tw_ACCESS_SECRET",
                    "tw_CONSUMER_KEY",
                    "tw_CONSUMER_SECRET",
                    "tw_text",
                    "url",
                ]:
                    self.assign_safe(field, conf)

    def load_image(self):
        image = None
        if self.pic:
            try:
                if self.pic.startswith("http"):
                    img_download = urllib.request.urlretrieve(self.pic)
                    self.pic = img_download[0]
                    image = Image.open(img_download[0], mode="r")
                elif os.path.isfile(self.pic):
                    image = Image.open(self.pic)
                else:
                    raise ValueError("image not found")
            except Exception as e:
                self.logger.error(e)
                exit(1)
            if self.do_show_pic:
                image.show()
                user_input = input("Confirm image? [Y/n] ")
                if user_input and user_input not in ("Y", "y"):
                    self.logger.warning("User aborted for wrong image.")
                    exit()
                self.do_show_pic = False

    def set_date_str(self):
        self.daterange_str = self.date_from + "-" + self.date_to
        today = date.today()
        self.publishdate_iso = today.strftime("%Y-%m-%d")
        self.publishdate_slash = today.strftime("%d/%m/%Y")
        self.publishdate_dot = today.strftime("%d.%m.%Y")
        self.publishdate_dotspace = today.strftime("%Y. %m. %d.")
        self.publishdate_dash = today.strftime("%d-%m-%Y")

    def create_texts(self):
        self.set_date_str()
        self.url = self.url.format(c=self)
        self.mail_body = self.mail_body.format(c=self)
        self.mail_subject = self.mail_subject.format(c=self)
        self.tw_text = self.tw_text.format(c=self)
        self.bluesky_text = self.bluesky_text.format(c=self)
        self.mail_from = self.mail_from.format(c=self)
        self.josm_body = self.josm_body.format(c=self)

    def check_url_exists(self):
        r = requests.get(self.url)
        return r.status_code == 200

    def send_stuff(self):
        self.create_texts()
        self.logger.info("Check if URL " + self.url + " exists before advertising...")
        if not self.check_url_exists():
            self.logger.error(
                "URL " + self.url + " seems to be wrong. Skipping " + self.lang
            )
            return False

        if self.do_bluesky:
            bluesky.post(self)
        if self.do_forum and self.forum_to:
            forum.post(self)
        if self.do_josm:
            josm.post(self)
        if self.do_lemmy:
            lemmy.post(self)
        if self.do_mail:
            mail.post(self)
        if self.do_mastodon:
            mastodon.post(self)
        if self.do_matrix:
            asyncio.run(matrix.post(self))
        if self.do_telegram:
            telegram.post(self)
        if self.do_twitter:
            twitter.post(self)

        return True
