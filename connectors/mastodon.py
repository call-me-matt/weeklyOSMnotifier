from mastodon import Mastodon
from PIL import Image


def login(self):
    return Mastodon(
        access_token=self.mastodon_TOKEN, api_base_url=self.mastodon_INSTANCE
    )


def upload_pic(self, mastodon):
    try:
        self.logger.debug("sending toot with image")
        pic = mastodon.media_post(self.pic)
        return [pic.id]
    except Exception as e:
        self.logger.error(f"failed to upload picture to Mastodon: {e}")
        # check if it is an animated gif (not supported by mastodon)
        try:
            image = Image.open(self.pic)
            if image.is_animated:
                self.logger.info("animated gif not supported, extracting frame")
                image.seek(0)
                image.save(self.pic + ".png", type="png")
                pic = mastodon.media_post(self.pic + ".png")
                return [pic.id]
        except:
            self.logger.error(
                f"failed to extract frame from animated gif. continuing without image. {e}"
            )
        return None


def pin_post(self, mastodon):
    try:
        if self.do_unpin_mastodon:
            for pinned_toot in mastodon.account_statuses(mastodon.me().id, pinned=True):
                self.logger.info(f"...unpinning previous toot {pinned_toot.id}")
                resp = mastodon.status_unpin(pinned_toot.id)
                self.logger.debug(f"{resp}")
        resp = mastodon.status_pin(toot.id)
        self.logger.info(f"...pinned toot")
        self.logger.debug(f"{resp}")
    except Exception as e:
        self.logger.error(f"failed to pin mastodon status: {e}")


def post(self):
    try:
        mastodon = self.login()
    except Exception as e:
        self.logger.error(f"could not connect to mastodon - {e}")
        return

    for recipient in self.mastodon_to:
        self.logger.info(f"...toot to {recipient}")
        media = None
        # upload picture if applicable
        if self.pic:
            media = self.upload_pic(mastodon)

        # toot!
        if self.lang == "int":
            # this is the public post (no receipients will be considered for 'int' language)
            try:
                toot = mastodon.status_post(
                    self.tw_text,
                    language=self.lang,
                    media_ids=media,
                    visibility="public",
                )
            except Exception as e:
                self.logger.error(f"failed to post to Mastodon, aborting. {e}")
                return False

            self.logger.debug(f"{toot}")
            # pin status
            if self.do_pin_mastodon:
                self.pin_post(mastodon)
        else:
            # send direct messages
            try:
                toot = mastodon.status_post(
                    self.tw_text + " " + recipient,
                    language=self.lang,
                    media_ids=media,
                    visibility="direct",
                )
            except Exception as e:
                self.logger.error(
                    f"failed to post direct message on Mastodon to {recipient}"
                )
