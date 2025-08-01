import re
from .base import Handler

class RegexFallbackHandler(Handler):
    def _handle(self, context):
        html = context.get("html", "")
        matches = re.findall(r"https?://[^\s\"']+\.m3u8", html)
        return matches[0] if matches else None

