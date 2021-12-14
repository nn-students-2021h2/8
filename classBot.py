import requests
import json
import workWithUser


class Bot:

    def __init__(self, token):
        self.TOKEN = token
        self.BASE_URL = f"https://api.telegram.org/bot{self.TOKEN}/"
        self.LONG_POLLING_TIMEOUT = 10
        self.last_update_id = None
        self.r = None

    def work(self):
        r = requests.get(self.BASE_URL + 'getUpdates',
                              params={
                                  'offset': self.last_update_id,
                                  'timeout': self.LONG_POLLING_TIMEOUT
                              })
        print(r.status_code)
        print(r.text)
        response_dict = json.loads(r.text)
        for upd in response_dict['result']:
            self.last_update_id = upd["update_id"] + 1
            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            if "text" in msg:
                result = workWithUser.work(msg["text"])
                r = requests.post(self.BASE_URL + 'sendMessage', params={
                    "chat_id": chat_id,
                    "text": result
                })
