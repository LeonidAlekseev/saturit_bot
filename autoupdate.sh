#!/bin/bash

cd /bin/saturit_bot
while true ; do
    git reset --hard HEAD
    git pull
    sleep 10
done