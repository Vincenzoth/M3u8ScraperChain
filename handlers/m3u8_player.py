from .base import Handler
from VLCPlayer import VLCPlayer

class M3U8PlayerHandler(Handler):
    def _handle(self, context):
        m3u8 = context.get("m3u8", "")
        referrer = context.get("referer_url", "")
        player = VLCPlayer(m3u8, referrer)
        # Avvia il flusso
        player.play_vlc()

        return None
