import re
import json
import requests
from .base import Handler

class ZiggoDeobfuscateHandler(Handler):
    def _handle(self, context):
        from strategy_loader import get_domain

        html = context.get("html", "")
        url = get_domain(context.get("url", "")) + "/server_lookup.php?channel_id="

        match = re.search(r'var channelKey = "(.+?)";', html)
        if match:
            try:
                channel_key = match.group(1)
                print("channelKey:", channel_key)
                url = "https://" + url + channel_key
                headers = {
                    "Referer": context.get("referer_url", ""),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                res = requests.get(url, headers=headers, timeout=5)
                res.raise_for_status()  # Solleva eccezione per codici 4xx/5xx

                data = res.json()  # Più sicuro di json.loads(res.text)

                server_key = data.get("server_key")
                if server_key:
                    if server_key == "top1/cdn":
                        m3u8 = f"https://top1.newkso.ru/top1/cdn/{channel_key}/mono.m3u8"
                    else:
                        m3u8 = f"https://{server_key}new.newkso.ru/{server_key}/{channel_key}/mono.m3u8"
                    context["m3u8"] = m3u8
                    context["referer_url"] = "https://" + get_domain(context.get("url", ""))
                    return context
                else:
                    print("⚠️ 'server_key' mancante nel JSON.")

            except requests.RequestException as e:
                print("❌ Errore HTTP:", e)
            except ValueError as e:
                print("❌ Errore nel parsing JSON:", e)
            except Exception as e:
                print("❌ Errore generico:", e)
        else:
            print("channelKey non trovato")

        return None

