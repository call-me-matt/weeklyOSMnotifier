from pythorhead import Lemmy


def post(self):

    self.logger.info(f"...lemmy.ml post...")

    try:
        lemmy = Lemmy("https://lemmy.ml", request_timeout=2)
        lemmy.log_in(self.lemmy_USER, self.lemmy_PW)
    except Exception as e:
        self.logger.error("failed to login to lemmy.ml - {e}")
        return

    try:
        community_id = lemmy.discover_community("openstreetmap")
    except Exception as e:
        self.logger.error("failed to discover openstreetmap community - {e}")
        return

    try:
        lemmy.post.create(community_id, self.tw_text)
    except Exception as e:
        self.logger.error("failed to discover openstreetmap community - {e}")
        return
