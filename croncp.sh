#!/usr/bin/bash

cat onedrawthema.sh    | sed -e "s/hogeuser/$USER/g" > ../cron/onedrawthema.sh
cat onedrawthema.plist | sed -e "s/hogeuser/$USER/g" > ~/Library/LaunchAgents/onedrawthema.plist

cat shiplist.sh        | sed -e "s/hogeuser/$USER/g" > ../cron/shiplist.sh
cat shiplist.plist     | sed -e "s/hogeuser/$USER/g" > ~/Library/LaunchAgents/shiplist.plist

launchctl setenv LANG ja_JP.UTF-8
launchctl setenv TWITTER_CONSUMER_KEY        "$TWITTER_CONSUMER_KEY"
launchctl setenv TWITTER_CONSUMER_SECRET     "$TWITTER_CONSUMER_SECRET"
launchctl setenv TWITTER_ACCESS_TOKEN_KEY    "$TWITTER_ACCESS_TOKEN_KEY"
launchctl setenv TWITTER_ACCESS_TOKEN_SECRET "$TWITTER_ACCESS_TOKEN_SECRET"

launchctl unload ~/Library/LaunchAgents/onedrawthema.plist
launchctl load   ~/Library/LaunchAgents/onedrawthema.plist

launchctl unload ~/Library/LaunchAgents/shiplist.plist
launchctl load   ~/Library/LaunchAgents/shiplist.plist

launchctl list | grep kancolle
