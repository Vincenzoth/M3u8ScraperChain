import requests
from bs4 import BeautifulSoup
from .base import Handler

class IframeHandler(Handler):
    def _handle(self, context):
        html = context.get("html", "")
        soup = BeautifulSoup(html, "html.parser")
        iframes = soup.find_all("iframe", src=True)
        for iframe in iframes:
            try:
                url = iframe["src"]
                headers = {
                    "Referer": context.get("referer_url", ""),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                res = requests.get(url, headers=headers, timeout=5, verify=False)
                if res:
                    context["referer_url"] = context["url"]
                    context["url"] = url
                    context["html"] = res.text
                    return context
            except Exception as e:
                continue
        return None

