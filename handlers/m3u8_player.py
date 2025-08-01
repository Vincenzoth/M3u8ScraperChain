from .base import Handler
import requests
import subprocess
import threading
import time
from pathlib import Path
from VLCPlayer import VLCPlayer

class M3U8PlayerHandler(Handler):
    def _handle(self, context):

        m3u8 = context.get("m3u8", "")

        # Inizializza e avvia il proxy
        proxy = VLCPlayer(m3u8, "", "")
        proxy.start_proxy()

        # Avvia VLC
        proxy.play_stream()
