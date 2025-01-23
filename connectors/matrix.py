from mautrix.client import ClientAPI


async def post(self):
    self.logger.info("...posting to matrix...")

    try:
        client = ClientAPI(
            self.matrix_USER, base_url=self.matrix_BASE, token=self.matrix_TOKEN
        )
    except Exception as e:
        self.logger.error(f"could not connect to matrix chat - {e}")
        return
    for recipient in self.matrix_to:
        self.logger.info(recipient)
        try:
            await client.send_text(recipient, self.tw_text)
        except Exception as e:
            self.logger.error(f"could not send matrix chat message- {e}")
    await client.api.session.close()
