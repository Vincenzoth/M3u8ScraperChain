from RojaScraping import RojaScraping
from CalcioStreaming import CalcioStreaming
from PlatinSport import PlatinSport
from oddspedia import Oddspedia
import requests

from strategy_loader import get_domain, build_chain_from_json

# os = Oddspedia()


# rs = RojaScraping()
# playble_events = rs.get_event_meta()
# while True:
#     meta_idx = int(input("Scegli una sorgente da 0 a " + str(len(playble_events))))
#     meta = playble_events[int(meta_idx)]
#     if ".mpd" in meta.url:
#         print("MPD")
#     elif meta.ace_url:
#         rs.play_ace(meta.ace_url, meta.referrer)
#     else:
#         rs.play(meta)
# # rs.url_render("https://tripplestream.com/juventus-vs-roma/", meta.p2p)
# rs.url_render(meta.play, meta.p2p)

# cs = CalcioStreaming()
# meta = cs.get_event_meta()
# cs.url_render(cs.url+meta.play, meta.p2p)

# ps = PlatinSport()
# meta = ps.get_event_meta()
# ps.play_ace(meta.ace_url, meta.referrer)

def extract_m3u8(url):
    print(f"[INFO] Scarico: {url}")
    res = requests.get(url, timeout=10)
    html = res.text

    domain = get_domain(url)
    chain = build_chain_from_json(domain)

    context = {
        "html": html,
        "url": url,
        "referer_url": url,
        "debug": True
    }
    m3u8 = chain.handle(context)

    if m3u8:
        print("[✔] Trovato:", m3u8)
    else:
        print("[✘] Nessun flusso trovato")

if __name__ == "__main__":
    test_url = "https://ziggo-gratis.com/raaz7/s756.php"
    extract_m3u8(test_url)