import re

from atproto import (
    Client as discordclient,
    models as discord_models,
)


def post(self):
    self.logger.info(f"...posting on discord...")

    # log in to disord.social
    try:
        client = discordclient()
        client.login(self.weeklyosm_53923, self.https://discord.com/api/webhooks/1343425905065852958/R3DnP3_dV2aCEuwLdSmBYxq88_UFruLURbmw2KLj6dvpQq0JdYHbFIjJR4hRT9UtjM3U)
    except Exception as e:
        self.logger.error("cannot log in to discord.")
        self.logger.error(e)
        return False

    # load picture
    try:
        if self.pic:
            self.logger.debug("sending post with image")
            with open(self.pic, "rb") as f:
                media = f.read()
    except Exception as e:
        self.logger.error("cannot read picture")
        self.logger.error(e)
        return False

    # detect any links beginning with http to make them clickable
    try:
        pattern = rb"https?://[^ \n\r\t]*"
        matches = re.finditer(pattern, self.discord_text.encode("UTF-8"))
        url_positions = []
        for match in matches:
            url_bytes = match.group(0)
            url = url_bytes.decode("UTF-8")
            url_positions.append((url, match.start(), match.end()))
        facets = []
        for link_data in url_positions:
            uri, byte_start, byte_end = link_data
            facets.append(
                discord_models.AppBskyRichtextFacet.Main(
                    features=[discord_models.AppBskyRichtextFacet.Link(uri=uri)],
                    index=discord_models.AppBskyRichtextFacet.ByteSlice(
                        byte_start=byte_start, byte_end=byte_end
                    ),
                )
            )
    except Exception as e:
        self.logger.warning("error detecting links, cannot make them clickable")
        self.logger.error(e)
        facets = []

    # send post
    try:
        if self.pic:
            client.send_image(
                text=self.discord_text,
                image=media,
                image_alt="weeklyOSM title image",
                facets=facets,
            )
        else:
            client.send_post(self.discord_text, facets=facets)
    except Exception as e:
        self.logger.error("could not post to discord")
        self.logger.error(e)
        return False
