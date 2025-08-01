import re
import base64
import requests
import warnings
from collections import Counter
from bs4 import BeautifulSoup
from models.model_event import Event, EventType, UrlRendered, MPDStream
from decoded_code import decode_obfuscated_code
from VLCPlayer import VLCPlayer
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo


class PlatinSport:

    def __init__(self):
        self.url = "https://www.platinsport.com/"  # Sostituisci con l'URL desiderato
        self.url_list = []
        self.referrer = ""
        self.m3u8_url = ""
        self.ace_url = ""
        self.mpd_stream = None


    def get_events(self, url):
        events = []
        try:
            # Effettua una richiesta GET all'URL
            response = requests.get(url)
            response.raise_for_status()  # Controlla se la richiesta è andata a buon fine

            # Analizza il contenuto HTML della pagina
            soup = BeautifulSoup(response.text, 'html.parser')

            # Trova il div con classe 'entry'
            entry_div = soup.find('div', class_='entry')

            # Trova il primo tag <a> al suo interno
            first_a = entry_div.find('a')

            # Prendi l'href
            if first_a and 'href' in first_a.attrs:
                match = re.search(r'https://.*', first_a['href'])
                if match:
                    url = match.group(0)
                    # Effettua una richiesta GET all'URL
                    response = requests.get(url)
                    response.raise_for_status()  # Controlla se la richiesta è andata a buon fine

                    # Analizza il contenuto HTML della pagina
                    soup = BeautifulSoup(response.text, 'html.parser')

                    div = soup.find('div', class_='myDiv1')

                    result = {}
                    current_key = None

                    for tag in div.children:
                        if tag.name == 'p':
                            # Iniziamo un nuovo blocco
                            league = tag.get_text(strip=True)
                            current_key = None
                        elif tag.name == 'time':
                            dt_utc = datetime.strptime(tag['datetime'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=ZoneInfo('UTC'))

                            # Sostituisci 'Europe/Rome' con il tuo fuso orario locale se diverso
                            dt_local = dt_utc.astimezone(ZoneInfo('Europe/Rome'))

                            formatted_time = dt_local.strftime('%d-%m-%Y %H:%M')
                            # Cerchiamo la stringa tipo "Venezia vs Fiorentina"
                            next_el = tag.next_sibling
                            match = ''
                            while next_el and (getattr(next_el, 'name', None) or str(next_el).strip() == ''):
                                next_el = next_el.next_sibling
                            if next_el and isinstance(next_el, str):
                                match = next_el.strip()
                            current_key = f"{league} - {formatted_time} - {match}"
                            result[current_key] = []
                        elif tag.name == 'a' and current_key:
                            href = tag.get('href')
                            if href:
                                name = tag.get_text(strip=True)
                                span_tag = tag.find('span')
                                flag_class = ' '.join(span_tag['class']) if span_tag and span_tag.has_attr(
                                    'class') else ''
                                lang = flag_class.split()[-1].split('-')[1]
                                if current_key:
                                    result[current_key].append({
                                        "name": name,
                                        "lang": lang,
                                        "href": href
                                    })

                        # Salva l'ultimo blocco, se presente


                # Output del dizionario
                for title, meta in result.items():
                    event_metas = []
                    for event_meta in meta:
                        event_meta = {
                            "p2p": "YES" if "acestream" in event_meta["href"] else "NO",
                            "name": event_meta["name"],
                            "lang": event_meta["lang"],
                            "event_type": "",
                            "kbps": "",
                            "play": event_meta["href"]
                        }
                        event_metas.append(EventType(**event_meta))
                    events.append(Event(title, event_metas))
            else:
                print("Nessun link trovato.")

        except requests.exceptions.RequestException as e:
            print(f"Errore durante il recupero dell'URL: {e}")

        return events


    def get_event_meta(self):
        self.events = self.get_events(self.url)
        for idx, event in enumerate(self.events):
            event.print_title(idx)
        self.event_idx = int(input("Scegli un evento da 0 a " + str(len(self.events))))
        event = self.events[self.event_idx]

        playble_events = []
        for idx, test_event in enumerate(event.event_metas):
            self.url_list = []
            self.m3u8_url = ""
            self.ace_url = ""
            self.referrer = ""

            self.url_render(test_event.play, test_event.p2p)
            if not self.m3u8_url == "" or self.ace_url:
                playble_events.append(UrlRendered(self.m3u8_url, self.ace_url, self.referrer))

        for idx, playble_event in enumerate(playble_events):
            playble_event.print_meta(idx)

        meta_idx = int(input("Scegli una sorgente da 0 a " + str(len(playble_events))))
        return playble_events[int(meta_idx)]


    def play(self, playable_event: UrlRendered):
        player = VLCPlayer(playable_event.url, playable_event.referrer)
        # Avvia il flusso
        player.play_vlc()

    def play_ace(self, ace_id, referrer):
        player = VLCPlayer(ace_id, referrer)
        # Avvia il flusso
        player.play_ace()

    def decode_base64(self, base64_string):
        # Decodifica della stringa
        decoded_bytes = base64.b64decode(base64_string)
        # Conversione da bytes a stringa
        return decoded_bytes.decode('utf-8')

    def url_render(self, url, p2p):
        # Conta le occorrenze
        counts = Counter(self.url_list)
        if any(count > 2 for count in counts.values()):
            return

        if p2p == "YES":
            self.ace_url = url
            self.url_list.append(self.ace_url)
