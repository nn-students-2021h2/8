def token():
    with open('token.txt') as f:  # create token.txt with your token
        return f.read()


# -*- coding: utf-8 -*-
TOKEN = token()  # Insert your bot token here - required!
# Optionally use an anonymizing proxy (SOCKS/HTTPS) if you encounter Telegram access issues in your region
PROXY = ''
