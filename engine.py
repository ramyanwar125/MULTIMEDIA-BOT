import os
import yt_dlp

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    # كوكيز قوية بصيغة Netscape
    cookie_content = (
        "# Netscape HTTP Cookie File\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\t__Secure-1PAPISID\t5i84Die2RJBNC2ce/AT2hauHxI6F92xPj_\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\t__Secure-1PSID\tg.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZJC__lOksy_V1shnK_eMU2QACgYKAWISARYSFQHGX2MiSRiVPtw6IQMxGYvEmCdH4RoVAUF8yKozwvkHQ0076\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\tLOGIN_INFO\tAFmmF2swRQIhAJr_X_MAu1PKtQ7YbEoBme3ow5NsWSDax1gAtpwPVsLsAiA7viGmF4Tmg5dEWSZDbAGU_wD1X0KD0dyQCM_i8udTOg:QUQ3MjNmd1paTG9Rdm8tekRXSWxDb292WEQwZVBpbEVwYWNDUlNfVGppVUJxQ1JWYzNoMGRsbFY3cHU1MjRfX0Zwb1J3SmhwU2xrekF4Q3lQY19RTWFvZ01qeDFmVHVScS04WVFOV29nQk5TOTdpUWhTa1VPd3hQSDBENThBUjYwbUlYMUNuNlZQaGFMZVJEajJHU21OZklkV2tKS1FTTFJR\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\tSID\tg.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZ6A00lT4BcAvf860P256R8QACgYKASISARYSFQHGX2MigyhtRA6u3mymovOefruTiBoVAUF8yKqXLVcp081Qmaiv3aJ2gJvh0076\n"
    )
    
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(cookie_content)
    return cookie_file

def get_all_formats(url):
    cookie_path = prepare_engine()
    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,
        'nocheckcertificate': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
                'player_skip': ['webpage', 'configs']
            }
        },
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}
            # استخراج الجودات التي تدعم الصوت والصورة معاً (MP4)
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res:
                        formats_btns[f"🎬 {res}p"] = f.get('format_id')
            
            # خيار احتياطي إذا لم يتم العثور على صيغ MP4 مباشرة
            if not formats_btns:
                formats_btns["🎬 Best Quality"] = "best"
                
            formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
            return formats_btns
        except Exception as e:
            print(f"Extraction Error: {e}")
            return {}

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'concurrent_fragment_downloads': 15,
        'continuedl': True,
        'buffersize': 1024 * 1024,
        'extractor_args': {'youtube': {'player_client': ['ios']}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
