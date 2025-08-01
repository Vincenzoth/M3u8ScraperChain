import re
import requests
from bs4 import BeautifulSoup
from models.model_event import Event, EventType
from VLCPlayer import VLCPlayer


class CalcioStreaming:

    def __init__(self):
        self.url = "https://calciostreaming.guru/"  # Sostituisci con l'URL desiderato

        response = requests.get(self.url, allow_redirects=False)

        if response.status_code == 301:
            self.url = response.headers.get("Location")

        self.url_list = []
        self.referrer = ""

    def get_events(self, url):
        events = []
        try:
            # Effettua una richiesta GET all'URL
            response = requests.get(url)
            response.raise_for_status()  # Controlla se la richiesta è andata a buon fine

            # Analizza il contenuto HTML della pagina
            soup = BeautifulSoup(response.text, 'html.parser')

            # Trova tutti i tag <a> nella pagina
            anchor_tags = soup.find_all('div', class_='panel panel-default')

            for index, tag in enumerate(anchor_tags, start=1):
                event_type = tag.find('h4').get_text(strip=True)
                table_row = tag.find_all('tr', class_=lambda x: x is None or 'audio' not in x)
                if len(table_row) > 0:
                    event_metas = []
                    for tr in table_row:
                        event_meta = {
                            "p2p": "NO",
                            "name": tr.find('a').get_text(strip=True),
                            "lang": "",
                            "event_type": event_type,
                            "kbps": "",
                            "play": tr.find('a')['href'],
                        }
                        event_metas.append(EventType(**event_meta))
                    events.append(Event(event_type, event_metas))
            print(f"{events}")  # strip=True rimuove spazi bianchi extra
        except requests.exceptions.RequestException as e:
            print(f"Errore durante il recupero dell'URL: {e}")

        return events

    def get_event_meta(self):
        self.events = self.get_events(self.url)
        for idx, event in enumerate(self.events):
            event.print_title(idx)
        self.event_idx = int(input("Scegli un evento da 0 a " + str(len(self.events))))
        event = self.events[self.event_idx]
        for idx, meta in enumerate(event.event_metas):
            meta.print_meta(idx)

        meta_idx = int(input("Scegli una sorgente da 0 a " + str(len(event.event_metas))))
        return event.event_metas[int(meta_idx)]

    def set_referrer(self):
        if len(self.url_list):
            self.referrer = re.search(r'https://(.+?)/', self.url_list[-1]).group()

    def play(self, m3u8_url, referrer, origin):
        # Inizializza e avvia il proxy
        proxy = VLCPlayer(m3u8_url, referrer, origin)
        proxy.start_proxy()

        # Avvia VLC
        proxy.play_stream()

    def url_render(self, url, p2p):
        self.set_referrer()
        self.url_list.append(url)
        response = requests.get(url, headers={
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            'Referer': self.referrer,
            'Origin': self.referrer[:-1]
        })

        soup = BeautifulSoup(response.text, 'html.parser')

        if '<iframe' in response.text:
            url = soup.find('iframe')['src']
            self.url_render(url, p2p)
        elif('<source' in response.text and '.m3u8' in response.text):
            url = soup.find('source')['src']
            self.url_render(url, p2p)
        elif 'source:' in response.text and '.m3u8' in response.text:
            url = re.search(r"source:\'(.+?)\'", response.text).group(1)
            self.url_render(url, p2p)
        elif "#EXTM3U\n#EXT-X-VERSION:3" in response.text:
            self.play(url, self.referrer, self.referrer[:-1])
        elif "#EXTM3U\n#EXT-X-STREAM-INF" in response.text:
            url = re.search(r"https(.+?)$", response.text).group(0)
            self.play(url, self.referrer, self.referrer[:-1])



