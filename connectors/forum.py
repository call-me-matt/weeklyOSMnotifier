import traceback
import requests
import time


def post(self):

    # only one message per language, as multiple posts with same text are rejected from forum

    self.logger.info(
        f"...community forum post to https://community.openstreetmap.org/t/-/{self.forum_to}"
    )

    try:
        FORUM_API = "https://community.openstreetmap.org/posts.json"

        data = {
            "title": self.mail_subject,
            "raw": self.mail_body,
            "topic_id": self.forum_to,
            "category": 0,
            "target_recipients": "",
            "target_usernames": "",
            "archetype": "",
            "created_at": "",
            "embed_url": "",
            "external_id": "",
        }

        headers = {
            "Content-Type": "application/json",
            "User-Api-Key": self.forum_KEY,
            "Accept": "application/json",
        }

        retries = 0
        while retries < 3:
            retries = retries + 1
            response = requests.post(FORUM_API, json=data, headers=headers)
            self.logger.debug(f"...json response: {response.json()}")
            if response.status_code == 200:
                if retries > 1:
                    self.logger.info("...erfolgreich!")
                break
            elif response.status_code == 429:
                # try again after a short wait time
                self.logger.warning(
                    "...abgelehnt (zu viele Posts). Probiere es in 30s erneut, bitte warten."
                )
                time.sleep(30)
            else:
                self.logger.error(
                    f"...fehlgeschlagen mit status code {response.status_code}"
                )
                break

        if response.status_code == 429:
            # error persists after last retry, show error and guidance:
            self.logger.error(
                f'...abgelehnt (zu viele Posts)! Probiere du es später noch einmal mit dem Befehl: ./runenvweekly2all.sh --forum "WEEKLY" "{self.lang}"'
            )

    except Exception as e:
        self.logger.error(f"failed to publish - {e}")
        traceback.print_exc()
