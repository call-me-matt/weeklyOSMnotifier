import telepot


def post(self):

    try:
        bot = telepot.Bot(self.telegram_TOKEN)
    except Exception as e:
        self.logger.error(f"could not connect to telegram - {e}")
        return

    for recipient in self.telegram_to:
        self.logger.info(f"...telegramming {recipient}")

        try:
            resp = bot.sendMessage(int(recipient), self.tw_text)
            self.logger.debug(resp)
        except Exception as e:
            self.logger.error(f"failed to send message to {recipient} - {e}")

    # pin message:
    # bot.unpinChatMessage(recipient) # unpins most recent chat message
    # bot.pinChatMessage(recipient,resp['message_id'],True)
