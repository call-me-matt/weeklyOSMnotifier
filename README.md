

# weeklyOSM "SPAM" Tool
This is the OSM Weekly "SPAM" Tool for sending updates in different languages. It supports posting to a forum,
sending emails via google and sending tweets via twitter. 
Feel free to use it as a baseline for simmilar usecases.


> Disclaimer:
> This script is _completely_ unsupported! It comes "as is" besides from request surrounding weeklyosm your issue-tickets or pull-requests will most likely be ignored.
> This software is unlicensed! For more information, please refer to <http://unlicense.org>

On linux run setup.sh to get you started with all requirements for a python environment. 

You should first edit configs/configs.yaml to your needs.
Note that by default all weekly_*.yaml files inherit their secrets from the file configs/secrets/weeklysecrets.yaml.
You would need to create that file looking something like this:

```
runnable: False
mail_user: 'somegmailusername'
mail_pw: somegmailssecretpasswort
tw_CONSUMER_KEY: "yourTwitterConsumerKey"
tw_CONSUMER_SECRET: "yourTwitterConsumerSecretFrdsfor09512kljda98324iu21as"
tw_ACCESS_KEY: "123456-YourTWAccessKeyNelsonMandela4Evaaaa"
tw_ACCESS_SECRET: "YourTWAccessSecretlsdkhjkahdkjahsrwqkjhqwkjhewqkjewqh"
``` 

Note that you have to enable sending e-mails via that account in your google-mail-account settings.

You can override the mail distribution lists with some private mail adress.
I.E. configs/mailto/weekly.pb could be created with the following content:

```
mail_to: 
 - "testaccout@gmail.com"
 - "someone@gmail.com"
 - "another@one.com"
 - "talk-pt@openstreetmap.org"
 - "talk-br@openstreetmap.org"
```

That would replace the mail_to: property from the file config/weekly_pb.yaml
leading to additional mail sent to the first three lines instead of only to the brasilian osm-lists.


For calling this from a script within the prepared environment call the shellscript runenvweekly2all.sh.
It takes the same parameters as the python script but fixes PYTHONIOENCODING to UTF-8 and LC_CTYPE to C.UFT-8 avoiding issues when called from node or other environments.


test call - for twitter
```
./runenvweekly2all.sh --twitter --twpic ~/downloads/C3wrVxcWcAEhtrU.jpg --showpic  "WEEKLYTWTEST" "en" "401" "7831" "2016" "02" "23.02.2016" "29.02.2016"
```

how to call - mail and twitter
```
./runenvweekly2all.sh --mail --twitter --twpic ~/Downloads/420_T_EN.jpg --showpic  "WEEKLY" "en" "420" "10586" "2018" "02" "2018-07-31" "2018-08-06"
```

INTRODUCING a new language xx 
1. in configs.yaml add two lines for the xx language
    - weekly_xx.yaml:
    - mailto/weekly_xx.yaml
2. in mailto 
    - create weekly_xx.yaml - content: email addresses
3. create weekly_xx.yaml - content: Twitter and email text

If you copy from another language ... DON'T forget to change the language_header