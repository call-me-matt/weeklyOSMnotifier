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

# recipient = -1001064379468
# message = "Hello from weeklyteam. We will notify you here about new issues of https://weeklyosm.eu from now on. Feedback welcome at info@weeklyosm.eu"
# try:
#     resp = bot.sendMessage(int(recipient), message)
#     print (resp)
# except Exception as e:
#     print (e)
