#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging

from utils import customformatter, configresolver


def main():

    # create logger
    logger = logging.getLogger("weeklyNotifier")
    logger.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(customformatter.CustomFormatter())
    logger.addHandler(ch)

    argparser = argparse.ArgumentParser(
        prog="weekly2all",
        description="Python 3 script to notify about a new issue of Wochennotiz/weeklyOSM.",
        epilog='example: python weekly2all.py --mail --forum --mastodon --pic ~/downloads/1.jpg "WEEKLY" "en,de"',
    )

    connector_group = argparser.add_argument_group(
        "Connectors", "list of services where announcements shall be made"
    )

    connector_group.add_argument(
        "--bluesky", action="store_true", help="send bluesky.social notification"
    )
    connector_group.add_argument(
        "--forum", action="store_true", help="send post to forum threads"
    )
    connector_group.add_argument(
        "--josm",
        action="store_true",
        help="send announcements to josm wiki (shown at josm program start)",
    )
    connector_group.add_argument(
        "--lemmy",
        action="store_true",
        help="send post to lemmy community",
    )
    connector_group.add_argument(
        "--mail", action="store_true", help="send e-mail notification"
    )
    connector_group.add_argument(
        "--mastodon", action="store_true", help="send mastodon notification"
    )
    connector_group.add_argument(
        "--matrix", action="store_true", help="send matrix chat notification"
    )
    connector_group.add_argument(
        "--telegram",
        action="store_true",
        help="send announcements to telegram channels and groups where the bot is admin",
    )
    connector_group.add_argument(
        "--twitter", action="store_true", help="send twitter notification"
    )

    argparser.add_argument(
        "--pic",
        help="picture source URL (local or web) for mastodon, bluesky and twitter. use 'auto' to retrieve from latest weekly",
    )

    argparser.add_argument(
        "--showpic", action="store_true", help="show picture before sending"
    )

    argparser.add_argument(
        "ctxt", choices=["WEEKLY", "WEEKLYTEST"], help="context and secrets for sending"
    )
    argparser.add_argument("lang", help="list of languages to publish")

    args = argparser.parse_args()

    logger.debug(args)

    cfr = configresolver.configResolver(logger, args)
    error_log = []

    for i, lang in enumerate(vars(args)["lang"].split(",")):
        logger.info(f"publishing {lang}...")

        config = cfr.configs.get((vars(args)["ctxt"], lang))
        if not config:
            logger.error(f"Sorry no matching config for <{lang}>. Available:")
            logger.info(f"{cfr.configs.keys()}")
        else:
            config.create_texts()
            logger.debug(f"{config}")
            # only show picture for first iteration:
            if i:
                config.do_show_pic = False
            if not config.send_stuff():
                error_log.append("failed to publish " + lang)
        for error in error_log:
            logger.critical(error)


if __name__ == "__main__":
    main()
