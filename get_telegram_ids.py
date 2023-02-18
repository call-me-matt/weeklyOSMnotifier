# this is a helper script to find out chat ids of telegram groups that
# have added our bot "theweeklyOSMbot" to their groups.

# How to use:
# source spamenv/bin/activate
# python get_telegram_ids.py
# deactivate

import telepot
import yaml

with open('configs/private/secrets/weeklysecrets.yaml') as f:
    # use safe_load instead load
    secrets = yaml.safe_load(f)

bot = telepot.Bot(secrets["telegram_TOKEN"])
resp = bot.getUpdates()

chats = []

for update in resp:
    try:
        info = update['message']['chat']
        if not info in chats:
            chats.append(info)
            print(info)
    except KeyError:
        continue
