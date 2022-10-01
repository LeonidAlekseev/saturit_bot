#!/bin/bash

cd /bin/saturit_bot
git reset --hard HEAD
git pull
python3 app.py
sleep 10
while true ; do
    git reset --hard HEAD
    git pull
    sleep 10
done