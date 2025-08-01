import re
from bs4 import BeautifulSoup
from .base import Handler

class ScriptTagHandler(Handler):
    def _handle(self, context):
        html = context.get("html", "")
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            if script.string and ".m3u8" in script.string:
                match = re.search(r"https?://[^\s\"']+\.m3u8", script.string)
                if match:
                    return match.group()
        return None

