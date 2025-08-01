import re


def to_base36(num):
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    while num > 0:
        num, remainder = divmod(num, 36)
        result = chars[remainder] + result
    return result or '0'


def decode_obfuscated_code(p, a, c, k):
    def e_func(c):
        # Questa funzione converte il valore numerico `c` in una stringa in base `a`
        return ('' if c < a else e_func(int(c / a))) + (chr(c + 29) if (c % a) > 35 else to_base36(c % a))

    # Creiamo la mappa di sostituzione
    d = {}
    for i in range(c - 1, -1, -1):
        d[e_func(i)] = e_func(i) if len(k[i]) == 0 else k[i]
    # Sostituiamo tutte le occorrenze nel codice offuscatoc
    for i in range(c):
        if (len(k) > i):
            p = re.sub(r'\b' + re.escape(e_func(i)) + r'\b', d[e_func(i)], p)
    return p


# Parametri originali dalla funzione JavaScript
p = '3 0;3 5={1n:y,E:y,O:Q,};3 8=g;3 7="t://F.J.o:n/m/l.k?s=j&e=h";4(w v!="C"&&w 9!="C"){4(9.z.K.M()){8=q;5["N"]=v.L()}S{7="t://T.P.o:n/m/l.k?s=j&e=h"}}$(I).H(2(){0=c x.B({G:7,D:"#0",R:"u%",V:"u%",W:{5:5,},1c:g,i:1d,1e:"1f",1g:"",U:"1",1b:"",1h:{1j:2(e){1k()},1l:2(e){A(2(){$(".a-r").d()},1m);4(!p){p=q}},1i:2(e){$(".a-r").1a()},19:2(e){$("#18-b").d()},17:2(){}}});4(8){9.z.16(0)}A(2(){0.f()},1)});2 15(){$(".a-14").13("12","11");3 6=0.10(0);6=c x.B(6.Z);0.Y();0=6;0.i();0.f();0.b()}2 X(){0.b()}'
a = 62
c = 86
k = "player||function|var|if|hlsjsConfig|newplayer|src|p2p|p2pml|stream|unmute|new|fadeOut||play|false|1727145495|mute|PeSwMtpa_tWgCtJhVhjJhA|m3u8|yxf1tlmsgek|hls|8443|net|videoStarted|true|logo||https|100|engine|typeof|Clappr|60|hlsjs|setTimeout|Player|undefined|parentId|maxBufferLength|cmxpfbya9zkeqdj32s57t6|source|ready|document|cdnrecruit|Engine|createLoaderClass|isSupported|loader|liveMaxLatencyDuration|cdnspectrum|Infinity|width|else|havnek3qzcwm25sdrbfjuy|position|height|playback|WSUnmute|destroy|options|configure|none|display|css|offline|WSreloadStream|initClapprPlayer|onReady|btn|onVolumeUpdate|fadeIn|watermarkLink|autoPlay|startMuted|stretching|bestfit|watermark|events|onPause|onError|errorPlaying|onPlay|1000|liveSyncDuration"