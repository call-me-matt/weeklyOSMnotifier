#!/bin/bash

set -eu

lang="en es ja cz fr pt pl de it ko zh tr cn"

if ! cmd=$(command -v curl)
then
  echo "please install curl"
  exit 1
fi

if (( $# == 0 ))
then
  feed="https://weeklyosm.eu/feed"
  article_id=$(curl -Ls "$feed" | grep "<link>https://weeklyosm.eu/archives/" | head -n 1 | cut -d "<" -f 2 | grep -o '[^/]*$')
else
  article_id=$1
fi
echo "checking for weekly https://weeklyosm.eu/archives/$article_id"

exit_code=0
for i in $lang
do
  article_url="https://weeklyosm.eu/$i/archives/$article_id"
  sourcecode=$(curl -Ls "$article_url")
  echo "$sourcecode" | grep "og:image" | grep "favicon" > /dev/random && echo "wrong share image for language $i in $article_url"
  no_of_leadpics=$(echo "$sourcecode" | grep 'alt="lead picture"' | wc -l)
  if [ $no_of_leadpics -ge 2 ]
  then
    echo "more than one lead picture ($no_of_leadpics) found for language $i in $article_url"
    exit_code=2
  fi
done

exit $exit_code

