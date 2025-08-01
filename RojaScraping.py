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

class RojaScraping:

    def __init__(self):
        self.url = "http://www.rojadirecta.eu/"  # Sostituisci con l'URL desiderato
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

            # Trova tutti i tag <a> nella pagina
            anchor_tags = soup.find_all('span', attrs={'itemscope': True})

            for index, tag in enumerate(anchor_tags, start=1):
                event_title = ""
                for child in tag.find(class_='menutitle').find_all('span'):
                    if('es' not in child.get('class', [])):
                        event_title += child.get_text(strip=True) + " "
                event_metas = []
                for child in tag.find(class_='submenu').find_all('tr')[1:]:
                    child = child.find_all('td')
                    event_meta = {
                        "p2p": child[0].get_text(strip=True),
                        "name": child[1].get_text(strip=True),
                        "lang": child[2].get_text(strip=True),
                        "event_type": child[3].get_text(strip=True),
                        "kbps": child[4].get_text(strip=True),
                        "play": child[5].find('a')['href'],
                    }
                    event_metas.append(EventType(**event_meta))
                events.append(Event(event_title, event_metas))
            print(f"{events}")  # strip=True rimuove spazi bianchi extra

        except requests.exceptions.RequestException as e:
            print(f"Errore durante il recupero dell'URL: {e}")

        return events

    def decode_eval_script(self, soup):
        scripts = soup.find_all('script')
        for script in scripts:
            if 'eval' in script.getText() and 'm3u8' in script.getText():
                encoded_data = re.findall(r"\('(.+?)'\)", script.getText())[1]
                p = re.search(r"^(.+?)'", encoded_data).group(1)
                a = re.search(r"',(\d+),", encoded_data).group(1)
                c = re.search(r",(\d+),'", encoded_data).group(1)
                k = re.search(r",'(.+?)'.split", encoded_data).group(1)
                return re.search(r'src="(.+?)"', decode_obfuscated_code(p, int(a), int(c), k.split('|'))).group(1)

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
            if "http://it.rojadirecta.eu/goto/" in test_event.play:
                test_event.play = test_event.play.replace("it.rojadirecta.eu/goto/", "")
            self.url_render(test_event.play, test_event.p2p)
            if not self.m3u8_url == "" or self.ace_url:
                playble_events.append(UrlRendered(self.m3u8_url, self.ace_url, self.referrer))

            try:
                print(str(idx)+" "+self.m3u8_url+" "+" "+test_event.play+" "+self.referrer + " "
                      + test_event.p2p + " " + test_event.name + " " + test_event.lang)
            except Exception as e:
                print(str(e))
        for idx, playble_event in enumerate(playble_events):
            playble_event.print_meta(idx)

        return playble_events

    def set_referrer(self, url, check_same_url=False):
        if len(self.url_list) > 0:
            self.referrer = re.search(r'https?://(.+?)/', self.url_list[-1]).group()
            base_url = re.search(r'https?://(.+?)/', url).group()
            if self.referrer == base_url and not check_same_url:
                for ref in reversed(self.url_list):
                    ref = re.search(r'https?://(.+?)/', ref).group()
                    if ref != base_url:
                        self.referrer = ref
                        return


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

        if self.m3u8_url == "":
            self.set_referrer(url)
            self.url_list.append(url)
        else:
            url = self.m3u8_url

        try:
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
            # print(url)
            response = requests.get(url, headers={
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
                'Referer': self.referrer,
                'Origin': self.referrer[:-1]

            }, verify=False, timeout=2)

            if response.status_code == 403:
                i = len(self.url_list) - 2
                while True:
                    self.referrer = re.search(r'https?://(.+?)/', self.url_list[i]).group()
                    response = requests.get(url, headers={
                        "User-Agent":
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
                        'Referer': self.referrer,
                        'Origin': self.referrer[:-1]
                    }, verify=False, timeout=2)
                    i = i - 1
                    if i == -1:
                        self.m3u8_url = ""
                        return
                    elif response.status_code == 200:
                        break
            elif response.status_code == 404:
                self.m3u8_url = ""
                return
            if "#EXTM3U\n#EXT-X-STREAM-INF" in response.text:
                if "CODECS" in response.text:
                    return
                else:
                    url = re.search(r"https(.+?)$", response.text).group(0)
                self.url_render(url + '.m3u8', p2p)
            elif "#EXT-X-VERSION:" in response.text:
                self.m3u8_url = url
                return

            soup = BeautifulSoup(response.text, 'html.parser')

            if p2p == 'NO':
                if "<script>eval(function(p,a,c,k,e,d)" in response.text:
                    self.m3u8_url = self.decode_eval_script(soup)
                    self.url_list.append(url)
                    self.set_referrer(url, True)
                elif "var playbackURL = " in response.text:
                    self.m3u8_url = re.search(r'var playbackURL = "(.+?)"', response.text).group(1)
                elif "P2PEngineHls" in response.text and "window.atob" in response.text:
                     base64_string = re.search(r"source: window.atob\((.+?)\)", response.text).group(1)
                     self.m3u8_url = self.decode_base64(base64_string)
                     if self.m3u8_url.startswith("//"):
                        self.m3u8_url = "https:" + self.m3u8_url
                elif 'source:' in response.text and '.m3u8' in response.text:
                    url = re.search(r"source: \'(.+?)\'", response.text).group(1)
                elif "P2PEngineHls.tryRegisterServiceWorker(p2pConfig)" in response.text:
                    url_to_join = re.search(r'return\s?\(\[(.+?)\]\.join\(\"\"\)', response.text).group(1)
                    # Trova tutti i contenuti tra doppi apici
                    url_to_join = re.findall(r'"(.*?)"', url_to_join)
                    url_joined = ''.join(utj for utj in url_to_join)
                    # Rimuovi gli escape extra (\)
                    url_decoded = url_joined.replace("\\/", "/")  # Sostituisci "\/" con "/"
                    url_decoded = url_decoded.replace("https:////", "https://")
                    self.m3u8_url = url_decoded
                    self.referrer = re.search(r'http?s://(.+?)/', url).group()
                elif "var playerInstance=jwplayer" in response.text:
                    self.m3u8_url = re.search(r'"file": \'(.+?)\'', response.text).group(1)
                    key_id = re.search(r'"keyId":"(.+?)"', response.text).group(1)
                    key = re.search(r'"key":"(.+?)"', response.text).group(1)
                    self.mpd_stream = MPDStream(self.m3u8_url, key_id, key)
                elif "<!-- body section -->" in response.text and "document.write(unescape(\"%3C" in response.text:
                    encoded_string = re.search(r'document.write\(unescape\(\"(.+?)\"', response.text).group(1)
                    decoded_string = urllib.parse.unquote(encoded_string)
                    url = re.search(r'type: "application\/x-mpegurl", src: \"(.+?)\"', decoded_string).group(1)
                    url = url.replace(' ', '%20')
                    if url.startswith("//"):
                        url = "http:" + url
                    self.m3u8_url = url
                elif "<!-- STREAM SOURCE -->" in response.text:
                    # Ottenere la base dell'URL
                    base_url = url[:url.rfind('/') + 1]
                    url = base_url + re.search(r'<!-- STREAM SOURCE -->.*?src="([^"]+)"', response.text, re.DOTALL).group(1)
                elif soup.find_all('iframe'):
                    base_url = url[:url.rfind('/') + 1]
                    if 'data-litespeed-src=' in response.text:
                        url = soup.find_all('iframe')[0]['data-litespeed-src']
                    else:
                        url = soup.find_all('iframe')[0]['src']
                    if url.startswith("//"):
                        url = "https:" + url
                    elif not url.startswith("https://") and not url.startswith("http://"):
                        url = base_url + url
                elif "<script>fid=" in response.text:
                    self.fid = re.search(r'fid="(.+?)"', response.text).group(1)
                    url = "https://"+re.search(r'src="//(.+?)"', response.text).group(1)
                elif "<ifr'+'ame src=" in response.text:
                    url = re.search(r'src="(.+?)"', response.text).group(1)
                    url = url.replace("'+ embedded +'", "desktop")
                    url = url.replace("'+ fid +'", self.fid)
                self.url_render(url, p2p)
            else:
                ace_id = re.search(r'ace\/manifest\.m3u8\?id=(.+?)"', response.text).group(1)
                self.ace_url = f"acestream://{ace_id}"
                return
        except Exception as e:
            print(e)
            return