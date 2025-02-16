from mautrix.client import ClientAPI


async def post(self):

    try:
        client = ClientAPI(
            self.matrix_USER, base_url=self.matrix_BASE, token=self.matrix_TOKEN
        )
    except Exception as e:
        self.logger.error(f"could not connect to matrix chat - {e}")
        return
    for recipient in self.matrix_to:
        self.logger.info(f"...posting to matrix chat: {recipient}")
        try:
            await client.send_text(recipient, self.tw_text)
        except Exception as e:
            self.logger.error(
                f"could not send matrix chat message to {recipient} - {e}"
            )
    await client.api.session.close()
