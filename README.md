

# weeklyOSM Notification Tool
This is the OSM Weekly Notification Tool for sending updates in different languages. It supports posting to a forum,
sending emails and toots and tweets. Feel free to use it as a baseline for simmilar usecases.


> Disclaimer:
> This software is unlicensed! For more information, please refer to <http://unlicense.org>

## installation

Clone this repo with submodules: `git clone --recurse-submodules git@github.com:call-me-matt/weeklyOSMnotifier.git`

On linux run setup.sh to get you started with all requirements for a python environment. 

First you should insert your secrets into the file `configs/private/secrets/weekly.yaml`.
You would need to create that file looking something like this:

```
runnable: False
bluesky_TOKEN: "x3xx-xyz-xyz-abcd"
bluesky_USER: "your@user.org"
forum_KEY: "abcdef123456"
josm_PW: "yourJosmWikiPass"
josm_USER: "yourJosmWikiUser"
mail_PW: "somegmailssecretpasswort"
mail_USER: "somegmailusername"
mastodon_INSTANCE: "yourinstance.social"
mastodon_TOKEN: "yourMastodonDeveloperApplicationAccessToken"
matrix_BASE: "https://matrix.org"
matrix_TOKEN: "syt_tokentoken_tokentoken_token"
matrix_USER: "@youruser:matrix.org"
telegram_TOKEN: "YourTelegramBotToken123:456"
tw_ACCESS_KEY: "123456-YourTWAccessKeyNelsonMandela4Evaaaa"
tw_ACCESS_SECRET: "YourTWAccessSecretlsdkhjkahdkjahsrwqkjhqwkjhewqkjewqh"
tw_BEARER_TOKEN: "AAAAAAAAAAabcdefg"
tw_CLIENT_ID: "abcdef123456xyz"
tw_CLIENT_SECRET: "123456abcdef789"
tw_CONSUMER_KEY: "0123456consumerkeyABC"
tw_CONSUMER_KEY: "yourTwitterConsumerKey"
tw_CONSUMER_SECRET: "yourTwitterConsumerSecretFrdsfor09512kljda98324iu21as"
```

Next you should define the recipients for each language in a `weekly_*.yaml` as defined in your `configs/configs.yaml`

```
mail_to: 
 - "testaccout@gmail.com"
 - "someone@gmail.com"
 - "another@one.com"
 - "talk-pt@openstreetmap.org"
 - "talk-br@openstreetmap.org"

 forum_to: "123456" # posts into https://community.openstreetmap.org/t/some-title/123456/
                    # only one thread possible per language due to forum's antispam

 telegram_to: # send telegram messages to the following recipients (if group, bot must be admin)
  - -123456789 # groups have negative identifiers
  - -987654321
 
 mastodon_to:  # send mastodon direct toots to the following recipients
  - "@user@instance"
  - "@other@instance"

```
## Adding a new language xx 

1. in your `configs.yaml` add two lines for the xx language
```
- weekly_xx.yaml:
  - private/mailto/weekly_xx.yaml
```
2. create `weekly_xx.yaml` in the `configs`-folder. content: text bodies of notifications in xx
3. in your `configs/private/mailto`-folder, create `weekly_xx.yaml`. content: notification recipients for xx

If you copy from another language, don't forget to change the language_header

## Utilization

For calling this from a script within the prepared environment call the shellscript `runenvweekly2all.sh`.
It takes the same parameters as the python script but fixes PYTHONIOENCODING to UTF-8 and LC_CTYPE to C.UFT-8 avoiding issues when called from node or other environments.


test call - for twitter
```
./runenvweekly2all.sh --twitter --pic ~/downloads/abc.jpg --showpic  "WEEKLYTEST" "en"
```

how weeklyOSM is announced:
```
./runenvweekly2all.sh --bluesky --forum --josm --mail --mastodon --matrix --telegram --pic auto --showpic  "WEEKLY" "int,de,en,es,pt,tr,ru,ja,fr,it,ko,br,zh,pl,uk"
```
