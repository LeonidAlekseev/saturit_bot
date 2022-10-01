# saturit_bot

1. run sudo apt update
2. run sudo apt install screen
3. clone git repository in /bin
4. run crontab -e and append
`@reboot export TELEGRAM_BOT_TOKEN=xxx && chmod +x /bin/saturit_bot/update_and_run.sh && /bin/saturit_bot/update_and_run.sh`