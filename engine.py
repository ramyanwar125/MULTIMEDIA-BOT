import os
import yt_dlp

def prepare_engine():
    cookie_file = "cookies.txt"
    # الكوكيز التي أرسلتها أنت سابقاً (بصيغة Netscape)
    raw_cookies = [
        {"n": "__Secure-1PAPISID", "v": "5i84Die2RJBNC2ce/AT2hauHxI6F92xPj_"},
        {"n": "__Secure-1PSID", "v": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZJC__lOksy_V1shnK_eMU2QACgYKAWISARYSFQHGX2MiSRiVPtw6IQMxGYvEmCdH4RoVAUF8yKozwvkHQM09piFqm1tD3qSe0076"},
        {"n": "LOGIN_INFO", "v": "AFmmF2swRQIhAJr_X_MAu1PKtQ7YbEoBme3ow5NsWSDax1gAtpwPVsLsAiA7viGmF4Tmg5dEWSZDbAGU_wD1X0KD0dyQCM_i8udTOg:QUQ3MjNmd1paTG9Rdm8tekRXSWxDb292WEQwZVBpbEVwYWNDUlNfVGppVUJxQ1JWYzNoMGRsbFY3cHU1MjRfX0Zwb1J3SmhwU2xrekF4Q3lQY19RTWFvZ01qeDFmVHVScS04WVFOV29nQk5TOTdpUWhTa1VPd3hQSDBENThBUjYwbUlYMUNuNlZQaGFMZVJEajJHU21OZklkV2tKS1FTTFJR"},
        {"n": "SID", "v": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZ6A00lT4BcAvf860P256R8QACgYKASISARYSFQHGX2MigyhtRA6u3mymovOefruTiBoVAUF8yKqXLVcp081Qmaiv3aJ2gJvh0076"}
    ]
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in raw_cookies:
            f.write(f".youtube.com\tTRUE\t/\tTRUE\t0\t{c['n']}\t{c['v']}\n")
    return cookie_file

def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(),
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = {}
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                res = f.get('height')
                if res: formats[f"🎬 {res}p"] = f.get('format_id')
        formats["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return formats

def run_download(url, f_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': f_id,
        'cookiefile': "cookies.txt",
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
