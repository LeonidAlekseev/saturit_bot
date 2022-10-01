#!/bin/bash

cd /bin/saturit_bot
while true ; do
      if [[ -f GITPULLMASTER ]] ; then
            git pull
      fi
      sleep 10
done