import requests


class Oddspedia:

    def __init__(self):
        url = "https://widgets.oddspedia.com/api/matches?api_token=6494c38100d8fc29e071a88ce5448bce271bca09a6408405812da903245b&lang=en"

        headers = {
            "User-Agent": "PostmanRuntime/7.28.4",
            "Accept": "*/*",
            "Host": "widgets.oddspedia.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        response = requests.get(url, headers=headers, verify=False)

        print(response.text)
