import subprocess
from flask import Flask, request, Response
import requests
from threading import Thread
import re


class VLCPlayer:

    def __init__(self, stream_url, referrer, origin=None):
        """
        Inizializza la classe VLCPlayer con i parametri necessari.

        :param vlc_path: Percorso dell'eseguibile di VLC
        :param m3u8_url: URL del flusso M3U8
        :param referrer: Referrer da passare nell'header HTTP
        :param user_agent: User-agent da passare nell'header HTTP
        """
        self.vlc_path = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
        self.ace_path = "C:\\Users\\vgior\\AppData\\Roaming\\ACEStream\\player\\ace_player.exe"
        self.stream_url = stream_url
        self.proxy_port = 8888
        self.referrer = referrer
        self.headers = {
            "Referer": referrer,
            "Origin": origin
        }
        self.app = Flask(__name__)
        self.configure_routes()

    def configure_routes(self):
        """Configura le route del proxy Flask."""

        @self.app.route("/proxy")
        def proxy():
            """Gestisce il file M3U8 e aggiorna i riferimenti ai segmenti."""
            try:
                # Scarica il file M3U8 dal server remoto con gli header personalizzati
                response = requests.get(self.stream_url, headers=self.headers)
                response.raise_for_status()

                # Modifica i riferimenti ai segmenti per passare attraverso il proxy
                m3u8_content = response.text
                modified_content = re.sub(
                    r"([a-zA-Z0-9\-]+\.ts)",  # Trova i segmenti .ts
                    lambda match: f"http://localhost:{self.proxy_port}/segment?url=https://live.servis.hair/hls/{match.group(0)}",
                    m3u8_content
                )
                return Response(modified_content, content_type="application/vnd.apple.mpegurl")
            except Exception as e:
                return f"Errore nel proxy M3U8: {e}", 500

        @self.app.route("/segment")
        def proxy_segment():
            """Gestisce le richieste ai segmenti `.ts`."""
            segment_url = request.args.get("url")
            if not segment_url:
                return "Errore: URL del segmento mancante", 400
            try:
                # Scarica il segmento dal server remoto con gli header personalizzati
                upstream_response = requests.get(segment_url, headers=self.headers, stream=True)
                return Response(
                    upstream_response.iter_content(chunk_size=1024),
                    content_type=upstream_response.headers.get("Content-Type"),
                    status=upstream_response.status_code
                )
            except Exception as e:
                return f"Errore nel proxy segmento: {e}", 500

    def start_proxy(self):
        """Avvia il server Flask in un thread separato."""
        thread = Thread(target=self.app.run, kwargs={"port": self.proxy_port, "debug": False})
        thread.daemon = True  # Chiude il thread quando il programma principale termina
        thread.start()

    def play_stream(self):
        """Avvia VLC con il flusso M3U8 passato dal proxy."""
        proxy_url = f"http://localhost:{self.proxy_port}/proxy"
        vlc_command = [self.vlc_path, proxy_url]
        try:
            subprocess.run(vlc_command, check=True)
        except FileNotFoundError:
            print("Errore: VLC non trovato. Assicurati che sia installato e nel PATH.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'esecuzione di VLC: {e}")

    def play_vlc(self):
        """
                Esegue il comando per avviare ACE con i parametri specificati.
                """
        command = [
            self.vlc_path,
            self.stream_url,
            f'--http-referrer={self.referrer}'
        ]
        try:
            subprocess.run(command, check=True)
            print("Flusso ACE avviato con successo.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'avvio di ACE: {e}")

    def play_ace(self):
        """
        Esegue il comando per avviare ACE con i parametri specificati.
        """
        command = [
            self.ace_path,
            self.stream_url,
            f'--http-referrer={self.referrer}'
        ]
        try:
            subprocess.run(command, check=True)
            print("Flusso ACE avviato con successo.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'avvio di ACE: {e}")
