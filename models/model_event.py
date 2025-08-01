class Event:
    def __init__(self, title, event_metas):
        self.title = title
        self.event_metas = event_metas

    def print_title(self, idx):
        print(str(idx)+' '+self.title)


class EventType:
    def __init__(self, p2p, name, lang, event_type, kbps, play ):
        self.p2p = p2p
        self.name = name
        self.lang = lang
        self.event_type = event_type
        self.kbps = kbps
        self.play = play

    def print_meta(self, idx):
        print(str(idx)+' '+self.p2p+' '+self.name+' '+self.lang+' '+self.event_type+' '+self.kbps+' '+self.play)


class UrlRendered:
    def __init__(self, url, ace_url, referrer):
        self.url = url
        self.ace_url = ace_url
        self.referrer = referrer

    def print_meta(self, idx):
        if self.ace_url:
            print(str(idx) + ' ' + self.ace_url + ' ' + self.referrer+' ACE')
        elif self.url is not None:
            print(str(idx)+' '+self.url+' '+self.referrer)


class MPDStream:
    def __init__(self, url, key_id, key):
        self.url = url
        self.key_id = key_id
        self.key = key
