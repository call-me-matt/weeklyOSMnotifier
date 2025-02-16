from mastodon import Mastodon


def post(self):
    try:
        mastodon = Mastodon(
            access_token=self.mastodon_TOKEN, api_base_url=self.mastodon_INSTANCE
        )
    except Exception as e:
        self.logger.error(f"could not connect to mastodon - {e}")
        return

    for recipient in self.mastodon_to:

        self.logger.info(f"...toot to {recipient}")

        media = None
        # upload picture if applicable
        if self.pic:
            self.logger.debug("sending toot with image")
            pic = mastodon.media_post(self.pic)
            media = [pic.id]

        # toot!
        if self.lang == "int":
            # this is the public post (no receipients will be considered for 'int' language)
            toot = mastodon.status_post(
                self.tw_text, language=self.lang, media_ids=media, visibility="public"
            )
            self.logger.debug(f"{toot}")
            # pin status
            if self.do_pin_mastodon:
                try:
                    if self.do_unpin_mastodon:
                        for pinned_toot in mastodon.account_statuses(
                            mastodon.me().id, pinned=True
                        ):
                            self.logger.info(
                                f"...unpinning previous toot {pinned_toot.id}"
                            )
                            resp = mastodon.status_unpin(pinned_toot.id)
                            self.logger.debug(f"{resp}")
                    resp = mastodon.status_pin(toot.id)
                    self.logger.info(f"...pinned toot")
                    self.logger.debug(f"{resp}")
                except Exception as e:
                    self.logger.error("failed to pin mastodon status:")
                    self.logger.error(e)
        else:
            # send direct messages
            toot = mastodon.status_post(
                self.tw_text + " " + recipient,
                language=self.lang,
                media_ids=media,
                visibility="direct",
            )
