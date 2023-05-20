#!/bin/bash

pip3 install -r requirements.txt

echo "BOT_TOKEN=YOUR_TOKEN" > .env
echo "ADMINS=ADMIN_ID,..." >> .env
