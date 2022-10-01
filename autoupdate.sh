#!/bin/bash

cd /home/user/www/example.com/repository
while true ; do
    git reset --hard HEAD
    git pull
    sleep 10
done