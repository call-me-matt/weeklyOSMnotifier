import re

from atproto import (
    Client as blueskyclient,
    models as bluesky_models,
)


def post(self):
    self.logger.info(f"...posting on bluesky")

    # log in to bluesky.social
    try:
        client = blueskyclient()
        client.login(self.bluesky_USER, self.bluesky_TOKEN)
    except Exception as e:
        self.logger.error("cannot log in to bluesky.")
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
        matches = re.finditer(pattern, self.bluesky_text.encode("UTF-8"))
        url_positions = []
        for match in matches:
            url_bytes = match.group(0)
            url = url_bytes.decode("UTF-8")
            url_positions.append((url, match.start(), match.end()))
        facets = []
        for link_data in url_positions:
            uri, byte_start, byte_end = link_data
            facets.append(
                bluesky_models.AppBskyRichtextFacet.Main(
                    features=[bluesky_models.AppBskyRichtextFacet.Link(uri=uri)],
                    index=bluesky_models.AppBskyRichtextFacet.ByteSlice(
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
                text=self.bluesky_text,
                image=media,
                image_alt="weeklyOSM title image",
                facets=facets,
            )
        else:
            client.send_post(self.bluesky_text, facets=facets)
    except Exception as e:
        self.logger.error("could not post to bluesky")
        self.logger.error(e)
        return False
