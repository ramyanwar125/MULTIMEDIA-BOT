import os
import yt_dlp

def prepare_engine():
    cookie_file = "cookies.txt"
    # الكوكيز التي أرسلتها سابقاً مدمجة بشكل صحيح
    raw_cookies = [
        {"domain": ".youtube.com", "name": "__Secure-1PAPISID", "value": "5i84Die2RJBNC2ce/AT2hauHxI6F92xPj_"},
        {"domain": ".youtube.com", "name": "__Secure-1PSID", "value": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZJC__lOksy_V1shnK_eMU2QACgYKAWISARYSFQHGX2MiSRiVPtw6IQMxGYvEmCdH4RoVAUF8yKozwvkHQM09piFqm1tD3qSe0076"},
        {"domain": ".youtube.com", "name": "__Secure-1PSIDCC", "value": "AKEyXzWmo8-Z2bAwuDl9fKbXSKykCPx1PE_zp9V4G0q6C2WFAqpGQ0xaQPBG6hxu2rH0Z1lisg"},
        {"domain": ".youtube.com", "name": "__Secure-1PSIDTS", "value": "sidts-CjQBflaCdXE2-yztonVseJnhKas1js-nf9LvvPwjgxqFACNi-SSNoXhO_OU84edTCdSiauxqEAA"},
        {"domain": ".youtube.com", "name": "__Secure-3PSID", "value": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZ05y0QhIe8xgocyhYKe2SugACgYKASUSARYSFQHGX2MisHeLhKQHWn7QRTzbZL8I2RoVAUF8yKpiTsXkm8_fZ16aC6KF9ReA0076"},
        {"domain": ".youtube.com", "name": "LOGIN_INFO", "value": "AFmmF2swRQIhAJr_X_MAu1PKtQ7YbEoBme3ow5NsWSDax1gAtpwPVsLsAiA7viGmF4Tmg5dEWSZDbAGU_wD1X0KD0dyQCM_i8udTOg:QUQ3MjNmd1paTG9Rdm8tekRXSWxDb292WEQwZVBpbEVwYWNDUlNfVGppVUJxQ1JWYzNoMGRsbFY3cHU1MjRfX0Zwb1J3SmhwU2xrekF4Q3lQY19RTWFvZ01qeDFmVHVScS04WVFOV29nQk5TOTdpUWhTa1VPd3hQSDBENThBUjYwbUlYMUNuNlZQaGFMZVJEajJHU21OZklkV2tKS1FTTFJR"},
        {"domain": ".youtube.com", "name": "SID", "value": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZ6A00lT4BcAvf860P256R8QACgYKASISARYSFQHGX2MigyhtRA6u3mymovOefruTiBoVAUF8yKqXLVcp081Qmaiv3aJ2gJvh0076"}
    ]
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in raw_cookies:
            f.write(f"{c['domain']}\tTRUE\t/\tTRUE\t0\t{c['name']}\t{c['value']}\n")
    return cookie_file

def get_all_formats(url):
    cookie_path = prepare_engine()
    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,
        'nocheckcertificate': True,
        # استخدام هوية تطبيق يوتيوب أندرويد الرسمي
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'user_agent': 'com.google.android.youtube/19.29.37 (Linux; U; Android 11) gzip',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}
            for f in info.get('formats', []):
                # نركز على جودات MP4 المباشرة
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res: formats_btns[f"🎬 {res}p"] = f.get('format_id')
            
            # إذا لم تتوفر جودات MP4 مدمجة، نطلب أفضل جودة متاحة
            if not formats_btns:
                formats_btns["🎬 Best Quality"] = "best"
                
            formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
            return formats_btns
        except:
            return {}

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': "cookies.txt",
        'nocheckcertificate': True,
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android']}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
