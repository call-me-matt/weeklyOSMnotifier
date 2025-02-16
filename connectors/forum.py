import traceback
import requests


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

        response = requests.post(FORUM_API, json=data, headers=headers)

        self.logger.info(f"...status code {response.status_code}")
        self.logger.debug(f"JSON Response: {response.json()}")

    except Exception as e:
        self.logger.error(f"failed to publish - {e}")
        traceback.print_exc()
