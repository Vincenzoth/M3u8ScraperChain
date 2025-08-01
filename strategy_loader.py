import json
from urllib.parse import urlparse
from handlers.m3u8_player import M3U8PlayerHandler
from handlers.script_tag import ScriptTagHandler
from handlers.regex_fallback import RegexFallbackHandler
from handlers.iframe import IframeHandler
from handlers.ziggo_deobfuscate import ZiggoDeobfuscateHandler

HANDLER_MAP = {
    "M3U8PlayerHandler": M3U8PlayerHandler,
    "ScriptTagHandler": ScriptTagHandler,
    "RegexFallbackHandler": RegexFallbackHandler,
    "IframeHandler": IframeHandler,
    "ZiggoDeobfuscateHandler": ZiggoDeobfuscateHandler
}

def load_strategy_config():
    with open("strategies.json", "r") as f:
        return json.load(f)

def get_domain(url):
    return urlparse(url).hostname or "default"

def build_chain_from_json(domain):
    config = load_strategy_config()
    steps = config.get(domain, config.get("default", []))

    if not steps:
        return None

    chain = HANDLER_MAP[steps[0]]()
    current = chain
    for step in steps[1:]:
        handler_class = HANDLER_MAP.get(step)
        if handler_class:
            current = current.set_next(handler_class())
    return chain
