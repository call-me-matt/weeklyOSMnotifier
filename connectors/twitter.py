import tweepy


def post(self):
    self.logger.info("...tweet")

    try:
        auth = tweepy.OAuthHandler(self.tw_CONSUMER_KEY, self.tw_CONSUMER_SECRET)
        auth.set_access_token(self.tw_ACCESS_KEY, self.tw_ACCESS_SECRET)
        api = tweepy.API(auth)

        twitterclient = tweepy.Client(
            consumer_key=self.tw_CONSUMER_KEY,
            consumer_secret=self.tw_CONSUMER_SECRET,
            access_token=self.tw_ACCESS_KEY,
            access_token_secret=self.tw_ACCESS_SECRET,
        )
    except Exception as e:
        self.logger.error(f"could not connect to twitter - {e}")
        return

    # update twitter status
    try:
        if self.pic:
            self.logger.debug("sending tweet with image")
            pic = api.media_upload(self.pic)
            twitterclient.create_tweet(
                text=self.tw_text, media_ids=[pic.media_id_string]
            )
        else:
            twitterclient.create_tweet(text=self.tw_text)
    except Exception as e:
        self.logger.error(f"could not tweet - {e}")
        return
